import asyncio
from argparse import Namespace
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, cast

from pytest_mock import MockerFixture
from starknet_py.net import KeyPair
from starknet_py.net.client_models import InvokeFunction, StarknetTransaction
from starknet_py.net.gateway_client import GatewayClient, Network
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

from protostar.cli.map_targets_to_file_paths import map_targets_to_file_paths
from protostar.commands import (
    BuildCommand,
    CallCommand,
    DeclareCommand,
    FormatCommand,
    InitCommand,
    InvokeCommand,
    MigrateCommand,
)
from protostar.commands.deploy_command import DeployCommand
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.commands.test import TestCommand
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.configuration_file import ConfigurationFileFactory
from protostar.formatter.formatter import Formatter
from protostar.formatter.formatting_result import (
    FormattingResult,
    format_formatting_result,
)
from protostar.formatter.formatting_summary import FormattingSummary
from protostar.io import log_color_provider
from protostar.io.input_requester import InputRequester
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_toml import ProtostarTOMLWriter
from protostar.self.protostar_directory import ProtostarDirectory
from protostar.starknet_gateway import Fee, GatewayFacade, GatewayFacadeFactory
from protostar.testing import TestingSummary


# pylint: disable=too-many-instance-attributes
class ProtostarFixture:
    def __init__(
        self,
        project_root_path: Path,
        init_command: InitCommand,
        build_command: BuildCommand,
        migrate_command: MigrateCommand,
        format_command: FormatCommand,
        declare_command: DeclareCommand,
        deploy_command: DeployCommand,
        test_command: TestCommand,
        invoke_command: InvokeCommand,
        call_command: CallCommand,
        transaction_registry: "TransactionRegistry",
    ) -> None:
        self._project_root_path = project_root_path
        self._init_command = init_command
        self._build_command = build_command
        self._migrate_command = migrate_command
        self._format_command = format_command
        self._declare_command = declare_command
        self._deploy_command = deploy_command
        self._test_command = test_command
        self._invoke_command = invoke_command
        self._transaction_registry = transaction_registry
        self._call_command = call_command

    @property
    def project_root_path(self) -> Path:
        return self._project_root_path

    def get_intercepted_transaction(
        self, index: int, expected_tx_type: "TransactionRegistry.KnownInterceptedTxType"
    ):
        transaction_registry = self._transaction_registry
        return transaction_registry.get_intercepted_transaction(index, expected_tx_type)

    async def declare(
        self,
        chain_id: Optional[StarknetChainId] = None,
        account_address: Optional[str] = None,
        contract: Optional[Path] = None,
        gateway_url: Optional[str] = None,
        wait_for_acceptance: Optional[bool] = False,
        max_fee: Optional[Fee] = None,
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
        args.max_fee = max_fee

        return await self._declare_command.run(args)

    async def deploy(
        self,
        contract: Path,
        gateway_url: Optional[str] = None,
        inputs: Optional[List[int]] = None,
    ):
        args = Namespace()
        args.contract = contract
        args.gateway_url = gateway_url
        args.inputs = inputs or []
        args.network = None
        args.token = None
        args.salt = None
        args.wait_for_acceptance = False
        args.chain_id = StarknetChainId.TESTNET
        return await self._deploy_command.run(args)

    async def test(
        self, targets: List[str], last_failed: bool = False
    ) -> TestingSummary:
        args = Namespace()
        args.target = targets
        args.ignore = []
        args.cairo_path = []
        args.disable_hint_validation = None
        args.no_progress_bar = None
        args.safe_collecting = None
        args.exit_first = None
        args.seed = None
        args.report_slowest_tests = 0
        args.last_failed = last_failed
        args.profiling = False

        return await self._test_command.run(args)

    def init_sync(self, project_name: str):
        args = Namespace()
        args.existing = False
        args.name = project_name
        result = asyncio.run(self._init_command.run(args))
        return result

    async def build(self):
        args = self._prepare_build_args()
        return await self._build_command.run(args)

    def build_sync(self):
        args = self._prepare_build_args()
        return asyncio.run(self._build_command.run(args))

    def _prepare_build_args(self):
        args = Namespace()
        args.compiled_contracts_dir = Path("./build")
        args.disable_hint_validation = False
        args.cairo_path = None
        return args

    async def migrate(
        self,
        path: Path,
        gateway_url: str,
        rollback: bool = False,
        account_address: Optional[str] = None,
    ):
        args = Namespace()
        args.path = path
        args.rollback = rollback
        args.no_confirm = True
        args.network = None
        args.gateway_url = gateway_url
        args.chain_id = StarknetChainId.TESTNET
        args.signer_class = None
        args.account_address = account_address
        args.private_key_path = None
        args.compiled_contracts_dir = Path() / "build"

        migration_history = await self._migrate_command.run(args)
        assert migration_history is not None
        return migration_history

    async def invoke(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[list[int]],
        gateway_url: str,
        account_address: Optional[str] = None,
        wait_for_acceptance: Optional[bool] = False,
        max_fee: Optional[Fee] = None,
    ):
        args = Namespace()
        args.contract_address = contract_address
        args.function = function_name
        args.inputs = inputs
        args.network = None
        args.gateway_url = gateway_url
        args.chain_id = StarknetChainId.TESTNET
        args.signer_class = None
        args.account_address = account_address
        args.private_key_path = None
        args.wait_for_acceptance = wait_for_acceptance
        args.max_fee = max_fee

        return await self._invoke_command.run(args)

    async def call(
        self,
        contract_address: int,
        function_name: str,
        inputs: Optional[list[int]],
        gateway_url: str,
    ):
        args = Namespace()
        args.contract_address = contract_address
        args.function = function_name
        args.inputs = inputs
        args.network = None
        args.gateway_url = gateway_url
        args.chain_id = StarknetChainId.TESTNET

        return await self._call_command.run(args)

    def format(
        self,
        targets: List[str],
        check: bool = False,
        verbose: bool = False,
        ignore_broken: bool = False,
    ) -> FormattingSummary:
        # We can't use run because it can raise a silent exception thus not returning summary.
        return self._format_command.format(targets, check, verbose, ignore_broken)

    def format_with_output(
        self,
        targets: List[str],
        check: bool = False,
        verbose: bool = False,
        ignore_broken: bool = False,
    ) -> Tuple[FormattingSummary, List[str]]:
        formatter = Formatter(self._project_root_path)

        output: List[str] = []
        callback: Callable[[FormattingResult], Any] = lambda result: output.append(
            format_formatting_result(result, check)
        )

        summary = formatter.format(
            file_paths=map_targets_to_file_paths(targets),
            check=check,
            verbose=verbose,
            ignore_broken=ignore_broken,
            on_formatting_result=callback,
        )

        return summary, output

    def create_files(
        self, relative_path_str_to_file: Dict[str, Union[str, Path]]
    ) -> None:
        for relative_path_str, file in relative_path_str_to_file.items():
            if isinstance(file, Path):
                content = file.read_text("utf-8")
            else:
                content = file
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
        func up(){{
            %{{
                {up_hint_content}
            %}}

            return ();
        }}

        @external
        func down(){{
            %{{
                {down_hint_content}
            %}}

            return ();
        }}
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


class TransactionRegistry:
    KnownInterceptedTxType = Literal["invoke"]

    def __init__(self) -> None:
        self._intercepted_txs: list[StarknetTransaction] = []

    def add(self, tx: StarknetTransaction):
        self._intercepted_txs.append(tx)

    def get_intercepted_transaction(
        self, index: int, expected_tx_type: KnownInterceptedTxType
    ):
        tx = self._intercepted_txs[index]
        if expected_tx_type == "invoke":
            assert isinstance(tx, InvokeFunction)
            return tx
        assert (
            False
        ), f"Couldn't find transaction (index={index}, expected_tx_type={expected_tx_type})"


class GatewayClientTxInterceptor(GatewayClient):
    def __init__(
        self, net: Network, transaction_registry: Optional[TransactionRegistry] = None
    ):
        super().__init__(net, session=None)
        self.intercepted_txs: list[StarknetTransaction] = []
        self._transaction_registry = transaction_registry

    async def _add_transaction(
        self,
        tx: StarknetTransaction,
        token: Optional[str] = None,
    ) -> dict:
        self.intercepted_txs.append(tx)
        if self._transaction_registry:
            self._transaction_registry.add(tx)
        return await super()._add_transaction(tx, token)


class TestFriendlyGatewayFacadeFactory(GatewayFacadeFactory):
    def __init__(
        self,
        project_root_path: Path,
        compiled_contract_reader: CompiledContractReader,
        transaction_registry: TransactionRegistry,
    ) -> None:
        super().__init__(project_root_path, compiled_contract_reader)
        self.recent_gateway_client: Optional[GatewayClientTxInterceptor] = None
        self._transaction_registry = transaction_registry

    def create(self, gateway_client: GatewayClient, logger: Optional[Logger]):
        gateway_client_tx_interceptor = GatewayClientTxInterceptor(
            # pylint: disable=protected-access
            net=gateway_client._net,
            transaction_registry=self._transaction_registry,
        )
        self.recent_gateway_client = gateway_client_tx_interceptor
        return GatewayFacade(
            project_root_path=self._project_root_path,
            compiled_contract_reader=self._compiled_contract_reader,
            gateway_client=gateway_client_tx_interceptor,
            logger=logger,
            log_color_provider=log_color_provider,
        )


def build_protostar_fixture(
    mocker: MockerFixture, project_root_path: Path, signing_credentials: Tuple[str, str]
):
    account_address, private_key = signing_credentials
    signer = StarkCurveSigner(
        account_address,
        KeyPair.from_private_key(int(private_key, 16)),
        StarknetChainId.TESTNET,
    )

    version_manager = mocker.MagicMock()
    version_manager.protostar_version = mocker.MagicMock()
    version_manager.protostar_version = "99.9.9"

    protostar_toml_writer = ProtostarTOMLWriter()

    configuration_file = ConfigurationFileFactory(
        active_profile_name=None, cwd=project_root_path
    ).create()
    project_cairo_path_builder = ProjectCairoPathBuilder(
        project_root_path=project_root_path, configuration_file=configuration_file
    )

    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        project_cairo_path_builder=project_cairo_path_builder,
        configuration_file=configuration_file,
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
        output_dir_path=project_root_path,
    )

    init_command = InitCommand(
        input_requester,
        new_project_creator=new_project_creator,
        adapted_project_creator=mocker.MagicMock(),
    )

    logger = getLogger()
    build_command = BuildCommand(logger=logger, project_compiler=project_compiler)

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

    transaction_registry = TransactionRegistry()

    gateway_facade_factory = TestFriendlyGatewayFacadeFactory(
        compiled_contract_reader=CompiledContractReader(),
        project_root_path=project_root_path,
        transaction_registry=transaction_registry,
    )

    migrate_command = MigrateCommand(
        migrator_builder=migrator_builder,
        log_color_provider=log_color_provider,
        logger=logger,
        requester=input_requester,
        gateway_facade_factory=gateway_facade_factory,
    )

    format_command = FormatCommand(
        project_root_path=project_root_path,
        logger=logger,
    )
    declare_command = DeclareCommand(
        logger=logger, gateway_facade_factory=gateway_facade_factory
    )

    deploy_command = DeployCommand(
        logger=logger, gateway_facade_factory=gateway_facade_factory
    )

    test_command = TestCommand(
        project_root_path=project_root_path,
        protostar_directory=ProtostarDirectory(project_root_path),
        project_cairo_path_builder=ProjectCairoPathBuilder(
            project_root_path,
            configuration_file=configuration_file,
        ),
        log_color_provider=log_color_provider,
        logger=logger,
        cwd=project_root_path,
        active_profile_name=None,
    )

    invoke_command = InvokeCommand(
        gateway_facade_factory=gateway_facade_factory, logger=logger
    )
    call_command = CallCommand(
        gateway_facade_factory=gateway_facade_factory, logger=logger
    )

    protostar_fixture = ProtostarFixture(
        project_root_path=project_root_path,
        init_command=init_command,
        call_command=call_command,
        build_command=build_command,
        migrate_command=migrate_command,
        format_command=format_command,
        declare_command=declare_command,
        deploy_command=deploy_command,
        test_command=test_command,
        invoke_command=invoke_command,
        transaction_registry=transaction_registry,
    )

    return protostar_fixture
