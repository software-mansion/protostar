import asyncio
from argparse import Namespace
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union, ContextManager, Tuple

import pytest
from starknet_py.net.models import StarknetChainId

from protostar.argument_parser import ArgumentParserFacade, CLIApp
from protostar.cli import MessengerFactory
from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from protostar.commands import (
    BuildCommand,
    BuildCairo1Command,
    CalculateAccountAddressCommand,
    CallCommand,
    DeclareCommand,
    FormatCommand,
    InitCommand,
    InitCairo1Command,
    InvokeCommand,
    MulticallCommand,
    DeclareCairo1Command,
)
from protostar.commands.cairo1_commands.test_cairo1_command import TestCairo1Command
from protostar.commands.deploy_account_command import DeployAccountCommand
from protostar.commands.deploy_command import DeployCommand
from protostar.commands.test import TestCommand
from protostar.commands.test.test_result_formatter import format_test_result
from protostar.formatter.formatting_result import FormattingResult
from protostar.formatter.formatting_summary import FormattingSummary
from protostar.io import log_color_provider
from protostar.starknet_gateway import Fee, Wei
from protostar.testing import TestingSummary
from protostar.starknet import Address
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.testing.test_results import TestResult
from tests.conftest import DevnetAccount

from .tokenizer import tokenize
from .transaction_registry import TransactionRegistry

ContractMap = Dict[str, list[str]]


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
class ProtostarFixture:
    def __init__(
        self,
        project_root_path: Path,
        init_command: InitCommand,
        init_cairo1_command: InitCairo1Command,
        build_command: BuildCommand,
        build_cairo1_command: BuildCairo1Command,
        format_command: FormatCommand,
        declare_command: DeclareCommand,
        declare_cairo1_command: DeclareCairo1Command,
        deploy_command: DeployCommand,
        test_command: TestCommand,
        test_cairo1_command: TestCairo1Command,
        invoke_command: InvokeCommand,
        call_command: CallCommand,
        deploy_account_command: DeployAccountCommand,
        calculate_account_address_command: CalculateAccountAddressCommand,
        multicall_command: MulticallCommand,
        cli_app: CLIApp,
        parser: ArgumentParserFacade,
        transaction_registry: TransactionRegistry,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._project_root_path = project_root_path
        self._init_command = init_command
        self._init_cairo1_command = init_cairo1_command
        self._build_command = build_command
        self._build_cairo1_command = build_cairo1_command
        self._format_command = format_command
        self._declare_command = declare_command
        self._declare_cairo1_command = declare_cairo1_command
        self._deploy_command = deploy_command
        self._test_command = test_command
        self._test_cairo1_command = test_cairo1_command
        self._invoke_command = invoke_command
        self._calculate_account_address_command = calculate_account_address_command
        self._transaction_registry = transaction_registry
        self._call_command = call_command
        self._deploy_account_command = deploy_account_command
        self._multicall_command = multicall_command
        self._cli_app = cli_app
        self._parser = parser
        self._monkeypatch = monkeypatch

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
        args = self._declare_common_args(
            contract=contract,
            account_address=account_address,
            chain_id=chain_id,
            gateway_url=gateway_url,
            wait_for_acceptance=wait_for_acceptance,
            max_fee=max_fee,
        )

        return await self._declare_command.run(args)

    async def declare_cairo1(
        self,
        contract: Path,
        compiled_class_hash: int,
        account_address: Optional[Address] = None,
        chain_id: Optional[StarknetChainId] = None,
        gateway_url: Optional[str] = None,
        wait_for_acceptance: Optional[bool] = False,
        max_fee: Optional[Fee] = None,
    ):
        args = self._declare_common_args(
            contract=contract,
            account_address=account_address,
            chain_id=chain_id,
            gateway_url=gateway_url,
            wait_for_acceptance=wait_for_acceptance,
            max_fee=max_fee,
        )
        args.compiled_class_hash = compiled_class_hash

        return await self._declare_cairo1_command.run(args)

    def _declare_common_args(
        self,
        contract: Path,
        account_address: Optional[Address] = None,
        chain_id: Optional[StarknetChainId] = None,
        gateway_url: Optional[str] = None,
        wait_for_acceptance: Optional[bool] = False,
        max_fee: Optional[Fee] = None,
    ) -> Namespace:
        args = Namespace()

        args.wait_for_acceptance = wait_for_acceptance
        args.chain_id = chain_id or StarknetChainId.TESTNET
        args.account_address = account_address
        args.contract = contract
        args.gateway_url = gateway_url
        args.max_fee = max_fee

        args.json = False
        args.signer_class = None
        args.private_key_path = None
        args.network = None
        args.token = None
        args.block_explorer = None

        return args

    async def deploy(
        self,
        class_hash: int,
        account_address: Optional[Address] = None,
        gateway_url: Optional[str] = None,
        inputs: Optional[CairoOrPythonData] = None,
        wait_for_acceptance: bool = False,
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
        args.wait_for_acceptance = wait_for_acceptance
        args.chain_id = StarknetChainId.TESTNET
        args.signer_class = None
        args.private_key_path = None
        args.account_address = int(account_address) if account_address else None
        args.json = False

        return await self._deploy_command.run(args)

    async def calculate_account_address(
        self,
        account_address_salt: int,
        account_class_hash: int,
        account_constructor_input: Optional[list[int]],
    ):
        args = self._parse(
            command_name="calculate-account-address",
            named_args={
                "account-class-hash": account_class_hash,
                "account-address-salt": account_address_salt,
                "account-constructor-input": account_constructor_input,
            },
        )
        return await self._calculate_account_address_command.run(args)

    async def deploy_account(
        self,
        account_address_salt: int,
        account_class_hash: int,
        max_fee: Wei,
        nonce: int,
        gateway_url: str,
        account_constructor_input: Optional[list[int]],
    ):
        args = self._parse(
            command_name="deploy-account",
            named_args={
                "gateway-url": gateway_url,
                "chain-id": StarknetChainId.TESTNET.value,
                "account-class-hash": account_class_hash,
                "max-fee": max_fee,
                "nonce": nonce,
                "account-address-salt": account_address_salt,
                "account-constructor-input": account_constructor_input,
            },
        )

        return await self._deploy_account_command.run(args)

    async def test(
        self, targets: list[str], last_failed: bool = False, estimate_gas: bool = False
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
        args.estimate_gas = estimate_gas

        return await self._test_command.run(args)

    def init_sync(self, project_name: str):
        args = Namespace()
        args.existing = False
        args.name = project_name
        result = asyncio.run(self._init_command.run(args))
        return result

    def init_cairo1_sync(self, project_name: str):
        args = Namespace()
        args.name = project_name
        result = asyncio.run(self._init_cairo1_command.run(args))
        return result

    async def build(self):
        args = self._prepare_build_args()
        return await self._build_command.run(args)

    def build_sync(self):
        args = self._prepare_build_args()
        return asyncio.run(self._build_command.run(args))

    async def build_cairo1(self):
        args = self._prepare_build_args()
        return await self._build_cairo1_command.run(args)

    def build_cairo1_sync(self):
        args = self._prepare_build_args()
        return asyncio.run(self._build_cairo1_command.run(args))

    def _prepare_build_args(self):
        args = Namespace()
        args.compiled_contracts_dir = Path("./build")
        args.disable_hint_validation = False
        args.cairo_path = None
        args.json = False
        args.contract_name = ""
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
        abi_path: Optional[Path] = None,
        json: bool = False,
    ):
        args = Namespace()
        args.contract_address = contract_address
        args.function = function_name
        args.inputs = inputs or []
        args.network = None
        args.gateway_url = gateway_url
        args.chain_id = StarknetChainId.TESTNET
        args.json = json
        args.abi = abi_path

        return await self._call_command.run(args)

    def format(
        self,
        targets: list[str],
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

    async def multicall(
        self,
        file_path: Path,
        account: DevnetAccount,
        gateway_url: str,
        json: bool = False,
    ):
        self._monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, account.private_key)
        result = await self._multicall_command.run(
            self._parse(
                command_name="multicall",
                positional_args=[file_path],
                named_args={
                    "account-address": account.address,
                    "gateway-url": gateway_url,
                    "chain-id": StarknetChainId.TESTNET.value,
                    "max-fee": "auto",
                    "json": json,
                },
            )
        )
        self._monkeypatch.delenv(PRIVATE_KEY_ENV_VAR_NAME)

        return result

    async def run_test_runner(
        self,
        target: Union[str, Path],
        cairo_path: Optional[list[Path]] = None,
    ) -> TestingSummary:
        """
        Runs test runner safely, without assertions on state of the summary and cache mechanism
        """
        if isinstance(target, Path):
            targets = [str(target)]
        else:
            targets = [target]

        def fake_indicator(_: str) -> ContextManager:
            ...

        messenger_factory = MessengerFactory(
            log_color_provider=log_color_provider,
            activity_indicator=fake_indicator,
        )

        return await self._test_command.test(
            targets=targets,
            messenger=messenger_factory.human(),
            cairo_path=cairo_path,
        )

    async def test_cairo1(
        self,
        target: Union[str, Path],
        linked_libraries: Optional[list[Tuple[Path, str]]] = None,
    ) -> TestingSummary:
        """
        Runs test runner safely, without assertions on state of the summary and cache mechanism
        """
        if isinstance(target, Path):
            targets = [str(target)]
        else:
            targets = [target]

        def fake_indicator(_: str) -> ContextManager:
            ...

        messenger_factory = MessengerFactory(
            log_color_provider=log_color_provider,
            activity_indicator=fake_indicator,
        )

        return await self._test_cairo1_command.test(
            targets=targets,
            messenger=messenger_factory.human(),
            linked_libraries=linked_libraries,
        )

    def _parse(
        self,
        command_name: str,
        positional_args: Optional[list[Any]] = None,
        named_args: Optional[dict[str, Any]] = None,
    ) -> Namespace:
        return self._parser.parse(
            [command_name] + tokenize(positional_args or [], named_args or {})
        )

    def format_test_result(self, test_result: TestResult) -> str:
        return format_test_result(test_result=test_result).format_human(
            log_color_provider
        )
