import asyncio
import os
from argparse import Namespace
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

from pytest_mock import MockerFixture
from starknet_py.net import KeyPair
from starknet_py.net.models import StarknetChainId

from protostar.cli.signable_command_util import PatchedStarkCurveSigner
from protostar.commands import (
    BuildCommand,
    DeclareCommand,
    FormatCommand,
    InitCommand,
    MigrateCommand,
)
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.formatter.formatter import Formatter
from protostar.formatter.formatting_result import (
    FormattingResult,
    format_formatting_result,
)
from protostar.formatter.formatting_summary import FormattingSummary
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_toml import (
    ProtostarContractsSection,
    ProtostarProjectSection,
    ProtostarTOMLReader,
    ProtostarTOMLWriter,
)
from protostar.utils.input_requester import InputRequester
from protostar.utils.log_color_provider import LogColorProvider


class ProtostarFixture:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        project_root_path: Path,
        init_command: InitCommand,
        build_command: BuildCommand,
        migrator_command: MigrateCommand,
        format_command: FormatCommand,
        declare_command: DeclareCommand,
    ) -> None:
        self._project_root_path = project_root_path
        self._init_command = init_command
        self._build_command = build_command
        self._migrator_command = migrator_command
        self._format_command = format_command
        self._declare_command = declare_command

    @property
    def project_root_path(self) -> Path:
        return self._project_root_path

    # pylint: disable=too-many-arguments
    async def declare(
        self,
        chain_id: Optional[int] = None,
        account_address: Optional[str] = None,
        contract: Optional[Path] = None,
        gateway_url: Optional[str] = None,
        wait_for_acceptance: Optional[bool] = False,
    ):
        args = Namespace()
        args.signer_class = None
        args.account_address = None
        args.private_key_path = None
        args.contract = None
        args.gateway_url = None
        args.network = None
        args.token = None
        args.wait_for_acceptance = wait_for_acceptance
        args.chain_id = chain_id
        args.account_address = account_address
        args.contract = contract
        args.gateway_url = gateway_url

        return await self._declare_command.run(args)

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
        account_address: Optional[str] = None,
    ):
        args = Namespace()
        args.path = path
        args.output_dir = output_dir
        args.rollback = rollback
        args.no_confirm = True
        args.network = None
        args.gateway_url = network
        args.chain_id = StarknetChainId.TESTNET.value
        args.signer_class = None
        args.account_address = account_address
        args.private_key_path = None
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
        callback: Callable[[FormattingResult], Any] = lambda result: output.append(
            format_formatting_result(result, check)
        )

        summary = formatter.format(
            targets=targets,
            check=check,
            verbose=verbose,
            ignore_broken=ignore_broken,
            on_formatting_result=callback,
        )

        return summary, output

    def create_files(self, relative_path_str_to_content: Dict[str, str]) -> None:
        for relative_path_str, content in relative_path_str_to_content.items():
            self._save_file(self._project_root_path / relative_path_str, content)

    def create_migration_file(
        self, up_hint_content: str = "", down_hint_content: str = ""
    ) -> Path:
        file_path = self._project_root_path / "migrations" / "migration_01_test.cairo"
        self._save_file(
            file_path,
            f"""
        %lang starknet

        @external
        func up():
            %{{
                {up_hint_content}
            %}}

            return ()
        end

        @external
        func down():
            %{{
                {down_hint_content}
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

    def get_project_root_path(self):
        return self._project_root_path


# pylint: disable=too-many-locals
def build_protostar_fixture(
    mocker: MockerFixture, project_root_path: Path, signing_credentials: Tuple[str, str]
):
    account_address, private_key = signing_credentials
    signer = PatchedStarkCurveSigner(
        account_address,
        KeyPair.from_private_key(int(private_key, 16)),
        StarknetChainId.TESTNET.value,
    )

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

    migrator_builder = Migrator.Builder(
        migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(
            project_compiler
        ),
        project_root_path=project_root_path,
    )
    migrator_builder.set_migration_execution_environment_config(
        MigratorExecutionEnvironment.Config(
            token=None,
        ),
    )

    migrator_builder.set_signer(signer)

    migrate_command = MigrateCommand(
        migrator_builder=migrator_builder,
        log_color_provider=log_color_provider,
        logger=logger,
        requester=input_requester,
        project_root_path=project_root_path,
    )

    format_command = FormatCommand(
        project_root_path=project_root_path,
        logger=logger,
    )
    declare_command = DeclareCommand(logger=logger, project_root_path=project_root_path)

    protostar_fixture = ProtostarFixture(
        project_root_path=project_root_path,
        init_command=init_command,
        build_command=build_command,
        migrator_command=migrate_command,
        format_command=format_command,
        declare_command=declare_command,
    )

    return protostar_fixture
