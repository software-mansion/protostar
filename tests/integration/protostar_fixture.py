import asyncio
import os
from argparse import Namespace
from logging import getLogger
from pathlib import Path
from typing import Dict, Optional, cast, List, Callable, Any, Tuple

from pytest_mock import MockerFixture

from protostar.commands import BuildCommand, InitCommand, MigrateCommand, FormatCommand
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.formatter.formatter import Formatter
from protostar.formatter.formatting_summary import FormattingSummary, format_summary
from protostar.formatter.formatting_result import FormattingResult, format_formatting_result
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
        format_command: FormatCommand,
    ) -> None:
        self._project_root_path = project_root_path
        self._init_command = init_command
        self._build_command = build_command
        self._migrator_command = migrator_command
        self._format_command = format_command

    @property
    def project_root_path(self) -> Path:
        return self._project_root_path

    def init_sync(self):
        args = Namespace()
        args.existing = False
        cwd = Path().resolve()
        os.chdir(self._project_root_path.parent)
        result = asyncio.run(self._init_command.run(args))
        os.chdir(cwd)
        return result

    def build_sync(self):
        args = Namespace()
        args.output = Path("./build")
        args.disable_hint_validation = False
        args.cairo_path = None
        return asyncio.run(self._build_command.run(args))

    async def migrate(
        self,
        path: Path,
        network: str,
        rollback=False,
        output_dir: Optional[Path] = None,
    ):
        args = Namespace()
        args.path = path
        args.output_dir = output_dir
        args.rollback = rollback
        args.no_confirm = True
        args.network = None
        args.gateway_url = network
        migration_history = await self._migrator_command.run(args)
        assert migration_history is not None
        return migration_history

    def format(
        self,
        targets: List[Path],
        check=False,
        verbose=False,
        ignore_broken=False,
    ) -> FormattingSummary:
        # We can't use run because it can raise a silent exception thus not returning summary.
        return self._format_command.format(targets, check, verbose, ignore_broken)

    def format_with_output(
        self,
        targets: List[Path],
        check=False,
        verbose=False,
        ignore_broken=False,
    ) -> Tuple[FormattingSummary, List[str]]:

        formatter = Formatter(self._project_root_path)

        output: List[str] = []
        callback = lambda result: output.append(format_formatting_result(result, check))

        summary = formatter.format(
            targets=targets,
            check=check,
            verbose=verbose,
            ignore_broken=ignore_broken,
            on_formatting_result_callback=callback,
        )

        return summary, output

    def create_files(self, relative_path_str_to_content: Dict[str, str]) -> None:
        for relative_path_str, content in relative_path_str_to_content.items():
            self._save_file(self._project_root_path / relative_path_str, content)

    def create_migration_file(self, hint_content: str) -> Path:
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

    def realtive_to_absolute_path(self, path_str: str):
        return self._project_root_path / path_str


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
        project_root_path=project_root_path,
    )

    migrate_command = MigrateCommand(
        migrator_builder=migrator_builder,
        log_color_provider=log_color_provider,
        logger=logger,
        requester=input_requester,
    )

    format_command = FormatCommand(
        project_root_path=project_root_path,
        logger=logger,
    )

    protostar_fixture = ProtostarFixture(
        project_root_path=project_root_path,
        init_command=init_command,
        build_command=build_command,
        migrator_command=migrate_command,
        format_command=format_command,
    )

    return protostar_fixture
