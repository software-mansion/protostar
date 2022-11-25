import asyncio
from argparse import Namespace
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, cast, Generator

from pytest_mock import MockerFixture
from starknet_py.net.client_models import InvokeFunction, StarknetTransaction
from starknet_py.net.gateway_client import GatewayClient, Network
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import DeployAccount

from protostar.argument_parser import ArgumentParserFacade, CLIApp
from protostar.cli import map_protostar_type_name_to_parser, MessengerFactory
from protostar.commands import (
    BuildCommand,
    CalculateAccountAddressCommand,
    CallCommand,
    DeclareCommand,
    FormatCommand,
    InitCommand,
    InvokeCommand,
)
from protostar.commands.deploy_account_command import DeployAccountCommand
from protostar.commands.deploy_command import DeployCommand
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.commands.test import TestCommand
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.configuration_file import (
    ConfigurationFileFactory,
    ConfigurationFileV2ContentFactory,
    ConfigurationTOMLContentBuilder,
)
from protostar.formatter.formatting_result import FormattingResult
from protostar.formatter.formatting_summary import FormattingSummary
from protostar.io import log_color_provider
from protostar.io.input_requester import InputRequester
from protostar.self.protostar_compatibility_with_project_checker import (
    parse_protostar_version,
)
from protostar.self.protostar_directory import ProtostarDirectory
from protostar.starknet_gateway import Fee, GatewayFacade, GatewayFacadeFactory
from protostar.starknet_gateway.gateway_facade import Wei
from protostar.testing import TestingSummary
from protostar.starknet import Address
from tests.conftest import Credentials
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.commands.call_command import SuccessfulCallMessage


# pylint: disable=too-many-instance-attributes
class ProtostarFixture:
    def __init__(
        self,
        project_root_path: Path,
        init_command: InitCommand,
        build_command: BuildCommand,
        format_command: FormatCommand,
        declare_command: DeclareCommand,
        deploy_command: DeployCommand,
        test_command: TestCommand,
        invoke_command: InvokeCommand,
        call_command: CallCommand,
        deploy_account_command: DeployAccountCommand,
        calculate_account_address_command: CalculateAccountAddressCommand,
        cli_app: CLIApp,
        parser: ArgumentParserFacade,
        transaction_registry: "TransactionRegistry",
    ) -> None:
        self._project_root_path = project_root_path
        self._init_command = init_command
        self._build_command = build_command
        self._format_command = format_command
        self._declare_command = declare_command
        self._deploy_command = deploy_command
        self._test_command = test_command
        self._invoke_command = invoke_command
        self._calculate_account_address_command = calculate_account_address_command
        self._transaction_registry = transaction_registry
        self._call_command = call_command
        self._deploy_account_command = deploy_account_command
        self._cli_app = cli_app
        self._parser = parser

    @property
    def project_root_path(self) -> Path:
        return self._project_root_path

    def get_intercepted_transactions_mapping(self):
        return self._transaction_registry

    async def declare(
        self,
        contract: Path,
        account_address: Optional[Address] = None,
        chain_id: Optional[StarknetChainId] = None,
        gateway_url: Optional[str] = None,
        wait_for_acceptance: Optional[bool] = False,
        max_fee: Optional[Fee] = None,
    ):
        args = Namespace()
        args.signer_class = None
        args.account_address = None
        args.private_key_path = None
        args.contract = contract
        args.gateway_url = None
        args.network = None
        args.token = None
        args.block_explorer = None
        args.wait_for_acceptance = wait_for_acceptance
        args.chain_id = chain_id or StarknetChainId.TESTNET
        args.account_address = account_address
        args.contract = contract
        args.gateway_url = gateway_url
        args.max_fee = max_fee
        args.json = False
        return await self._declare_command.run(args)

    async def deploy(
        self,
        class_hash: int,
        gateway_url: Optional[str] = None,
        inputs: Optional[CairoOrPythonData] = None,
        max_fee: Optional[Fee] = None,
    ):
        args = Namespace()
        args.class_hash = class_hash
        args.gateway_url = gateway_url
        args.max_fee = max_fee
        args.inputs = inputs or []
        args.network = None
        args.token = None
        args.salt = None
        args.block_explorer = None
        args.wait_for_acceptance = False
        args.chain_id = StarknetChainId.TESTNET
        args.signer_class = None
        args.private_key_path = None
        args.account_address = None
        args.json = False

        return await self._deploy_command.run(args)

    async def calculate_account_address(
        self,
        account_address_salt: int,
        account_class_hash: int,
        account_constructor_input: Optional[list[int]],
    ):
        args = self._parser.parse(
            [
                "calculate-account-address",
                "--account-class-hash",
                str(account_class_hash),
                "--account-address-salt",
                str(account_address_salt),
            ]
            + (
                [
                    "--account-constructor-input",
                    " ".join(str(i) for i in account_constructor_input),
                ]
                if account_constructor_input
                else []
            )
        )
        return await self._calculate_account_address_command.run(args)

    async def deploy_account(
        self,
        account_address: Address,
        account_address_salt: int,
        account_class_hash: int,
        max_fee: Wei,
        nonce: int,
        gateway_url: str,
        account_constructor_input: Optional[list[int]],
    ):
        args = self._parser.parse(
            [
                "deploy-account",
                "--account-address",
                str(account_address),
                "--gateway-url",
                gateway_url,
                "--chain-id",
                str(StarknetChainId.TESTNET.value),
                "--nonce",
                str(nonce),
                "--account-class-hash",
                str(account_class_hash),
                "--max-fee",
                str(max_fee),
                "--account-address-salt",
                str(account_address_salt),
            ]
            + (
                [
                    "--account-constructor-input",
                    " ".join(str(i) for i in account_constructor_input),
                ]
                if account_constructor_input
                else []
            )
        )

        return await self._deploy_account_command.run(args)

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
        args.max_steps = None

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
        args.json = False
        return args

    async def invoke(
        self,
        contract_address: Address,
        function_name: str,
        inputs: Optional[CairoOrPythonData],
        gateway_url: str,
        account_address: Optional[Address] = None,
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
        args.block_explorer = None
        args.wait_for_acceptance = wait_for_acceptance
        args.max_fee = max_fee
        args.json = False

        return await self._invoke_command.run(args)

    async def call(
        self,
        contract_address: Address,
        function_name: str,
        inputs: Optional[CairoOrPythonData],
        gateway_url: str,
    ) -> SuccessfulCallMessage:
        args = Namespace()
        args.contract_address = contract_address
        args.function = function_name
        args.inputs = inputs
        args.network = None
        args.gateway_url = gateway_url
        args.chain_id = StarknetChainId.TESTNET
        args.json = False

        return await self._call_command.run(args)

    def format(
        self,
        targets: List[str],
        check: bool = False,
        verbose: bool = False,
        ignore_broken: bool = False,
        on_formatting_result: Optional[Callable[[FormattingResult], Any]] = None,
    ) -> FormattingSummary:
        # We can't use run because it can raise a silent exception thus not returning summary.
        return self._format_command.format(
            targets=targets,
            check=check,
            verbose=verbose,
            ignore_broken=ignore_broken,
            on_formatting_result=on_formatting_result,
        )

    def create_files(
        self, relative_path_str_to_file: Dict[str, Union[str, Path]]
    ) -> None:
        for relative_path_str, file in relative_path_str_to_file.items():
            if isinstance(file, Path):
                content = file.read_text("utf-8")
            else:
                content = file
            self._save_file(self._project_root_path / relative_path_str, content)

    @staticmethod
    def _save_file(path: Path, content: str) -> None:
        path.parent.mkdir(exist_ok=True, parents=True)
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(content)


@dataclass
class TransactionRegistry:
    invoke_txs: list[InvokeFunction] = field(default_factory=list)
    deploy_account_txs: list[DeployAccount] = field(default_factory=list)

    def register(self, tx: StarknetTransaction):
        if isinstance(tx, InvokeFunction):
            self.invoke_txs.append(tx)
        if isinstance(tx, DeployAccount):
            self.deploy_account_txs.append(tx)


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
            self._transaction_registry.register(tx)
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

    def create(self, gateway_client: GatewayClient):
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
        )


@contextmanager
def fake_activity_indicator(message: str) -> Generator[None, None, None]:
    yield


def build_protostar_fixture(
    mocker: MockerFixture,
    project_root_path: Path,
):
    version_manager = mocker.MagicMock()
    version_manager.protostar_version = mocker.MagicMock()
    version_manager.protostar_version = "99.9.9"

    configuration_file = ConfigurationFileFactory(
        active_profile_name=None, cwd=project_root_path
    ).create()
    project_cairo_path_builder = ProjectCairoPathBuilder(
        project_root_path=project_root_path,
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

    configuration_file_content_factory = ConfigurationFileV2ContentFactory(
        content_builder=ConfigurationTOMLContentBuilder()
    )

    new_project_creator = NewProjectCreator(
        script_root=Path(__file__).parent / ".." / "..",
        requester=input_requester,
        configuration_file_content_factory=configuration_file_content_factory,
        protostar_version=parse_protostar_version("0.0.0"),
        output_dir_path=project_root_path,
    )

    init_command = InitCommand(
        input_requester,
        new_project_creator=new_project_creator,
        adapted_project_creator=mocker.MagicMock(),
    )

    messenger_factory = MessengerFactory(
        log_color_provider=log_color_provider,
        activity_indicator=fake_activity_indicator,
    )

    build_command = BuildCommand(
        project_compiler=project_compiler,
        messenger_factory=messenger_factory,
    )

    transaction_registry = TransactionRegistry()

    gateway_facade_factory = TestFriendlyGatewayFacadeFactory(
        compiled_contract_reader=CompiledContractReader(),
        project_root_path=project_root_path,
        transaction_registry=transaction_registry,
    )

    deploy_account_command = DeployAccountCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    format_command = FormatCommand(
        project_root_path=project_root_path,
        messenger_factory=messenger_factory,
    )
    declare_command = DeclareCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    deploy_command = DeployCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    test_command = TestCommand(
        project_root_path=project_root_path,
        protostar_directory=ProtostarDirectory(project_root_path),
        project_cairo_path_builder=ProjectCairoPathBuilder(
            project_root_path,
        ),
        log_color_provider=log_color_provider,
        cwd=project_root_path,
        active_profile_name=None,
    )

    invoke_command = InvokeCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )
    call_command = CallCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    calculate_account_address_command = CalculateAccountAddressCommand(
        messenger_factory=messenger_factory
    )

    cli_app = CLIApp(
        commands=[
            deploy_account_command,
            calculate_account_address_command,
        ]
    )
    parser = ArgumentParserFacade(
        cli_app, parser_resolver=map_protostar_type_name_to_parser
    )

    protostar_fixture = ProtostarFixture(
        project_root_path=project_root_path,
        init_command=init_command,
        call_command=call_command,
        build_command=build_command,
        format_command=format_command,
        declare_command=declare_command,
        deploy_command=deploy_command,
        test_command=test_command,
        invoke_command=invoke_command,
        deploy_account_command=deploy_account_command,
        cli_app=cli_app,
        parser=parser,
        transaction_registry=transaction_registry,
        calculate_account_address_command=calculate_account_address_command,
    )

    return protostar_fixture
