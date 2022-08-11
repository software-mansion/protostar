from argparse import Namespace
from logging import getLogger
from pathlib import Path
from typing import Dict, cast

from pytest_mock import MockerFixture

from protostar.commands import BuildCommand, InitCommand, MigrateCommand
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_toml import (
    ProtostarContractsSection,
    ProtostarProjectSection,
    ProtostarTOMLReader,
    ProtostarTOMLWriter,
)
from protostar.starknet_gateway import GatewayFacade
from protostar.utils.input_requester import InputRequester
from protostar.utils.log_color_provider import LogColorProvider


class ProtostarFixture:
    def __init__(
        self,
        project_root_path: Path,
        init_command: InitCommand,
        build_command: BuildCommand,
        migrator_command: MigrateCommand,
    ) -> None:
        self._project_root_path = project_root_path
        self._init_command = init_command
        self._build_command = build_command
        self._migrator_command = migrator_command

    async def init(self):
        args = Namespace()
        args.existing = False
        return await self._init_command.run(args)

    async def build(self):
        args = Namespace()
        args.output = Path("./build")
        args.disable_hint_validation = False
        args.cairo_path = None
        return await self._build_command.run(args)

    async def migrate(self, path: Path, network: str, rollback=False):
        args = Namespace()
        args.path = path
        args.output_dir = None
        args.rollback = rollback
        args.no_confirm = True
        args.network = None
        args.gateway_url = network
        migration_history = await self._migrator_command.run(args)
        assert migration_history is not None
        return migration_history

    def create_files(self, relative_path_str_to_content: Dict[str, str]) -> None:
        for relative_path_str, content in relative_path_str_to_content.items():
            self._save_file(self._project_root_path / relative_path_str, content)

    def create_migration(self, hint_content: str) -> Path:
        file_path = self._project_root_path / "migrations" / "migration_01_test.cairo"
        self._save_file(
            file_path,
            f"""
        %lang starknet

        @external
        func up():
            %{{
                {hint_content}
            %}}

            return ()
        end
        """,
        )
        return file_path

    @staticmethod
    def _save_file(path: Path, content: str) -> None:
        path.parent.mkdir(exist_ok=True, parents=True)
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(content)


# pylint: disable=too-many-locals
def build_protostar_fixture(mocker: MockerFixture, project_root_path: Path):

    version_manager = mocker.MagicMock()
    version_manager.protostar_version = mocker.MagicMock()
    version_manager.protostar_version = "99.9.9"

    protostar_toml_path = project_root_path / "protostar.toml"
    protostar_toml_writer = ProtostarTOMLWriter()
    protostar_toml_reader = ProtostarTOMLReader(protostar_toml_path=protostar_toml_path)

    project_cairo_path_builder = ProjectCairoPathBuilder(
        project_root_path=project_root_path,
        project_section_loader=ProtostarProjectSection.Loader(protostar_toml_reader),
    )

    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        project_cairo_path_builder=project_cairo_path_builder,
        contracts_section_loader=ProtostarContractsSection.Loader(
            protostar_toml_reader
        ),
    )

    migrator_builder = Migrator.Builder(
        migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(),
        gateway_facade_builder=GatewayFacade.Builder(project_root_path),
    )

    input_requester = cast(InputRequester, mocker.MagicMock())

    def request_input(message: str) -> str:
        if message.startswith("project directory name"):
            return project_root_path.name
        if message.startswith("libraries directory name"):
            return "lib"
        return ""

    input_requester.request_input = request_input

    new_project_creator = NewProjectCreator(
        script_root=Path(__file__).parent / ".." / "..",
        requester=input_requester,
        protostar_toml_writer=protostar_toml_writer,
        version_manager=version_manager,
        output_dir_path=project_root_path.parent,
    )

    init_command = InitCommand(
        input_requester,
        new_project_creator=new_project_creator,
        adapted_project_creator=mocker.MagicMock(),
    )

    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        project_cairo_path_builder=project_cairo_path_builder,
        contracts_section_loader=ProtostarContractsSection.Loader(
            protostar_toml_reader
        ),
    )

    logger = getLogger()
    build_command = BuildCommand(logger=logger, project_compiler=project_compiler)

    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = True

    gateway_facade_builder = GatewayFacade.Builder(project_root_path=project_root_path)

    migrator_builder = Migrator.Builder(
        gateway_facade_builder=gateway_facade_builder,
        migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(),
    )

    migrate_command = MigrateCommand(
        migrator_builder=migrator_builder,
        log_color_provider=log_color_provider,
        logger=logger,
        requester=input_requester,
    )

    protostar_fixture = ProtostarFixture(
        project_root_path=project_root_path,
        init_command=init_command,
        build_command=build_command,
        migrator_command=migrate_command,
    )

    return protostar_fixture
