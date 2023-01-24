import asyncio
from argparse import Namespace
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, ContextManager

import pytest
from starknet_py.net.models import StarknetChainId

from protostar.argument_parser import ArgumentParserFacade, CLIApp
from protostar.cli import MessengerFactory
from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from protostar.commands import (
    BuildCommand,
    CalculateAccountAddressCommand,
    CallCommand,
    DeclareCommand,
    FormatCommand,
    InitCommand,
    InvokeCommand,
    MulticallCommand,
)
from protostar.commands.deploy_account_command import DeployAccountCommand
from protostar.commands.deploy_command import DeployCommand
from protostar.commands.test import TestCommand
from protostar.configuration_file import (
    ConfigurationFileV2Model,
    ConfigurationFileV2,
    ConfigurationTOMLContentBuilder,
    ConfigurationFileV2ContentFactory,
)
from protostar.configuration_file.configuration_toml_interpreter import (
    ConfigurationTOMLInterpreter,
)
from protostar.formatter.formatting_result import FormattingResult
from protostar.formatter.formatting_summary import FormattingSummary
from protostar.io import log_color_provider
from protostar.starknet_gateway import Fee, Wei
from protostar.testing import TestingSummary
from protostar.starknet import Address
from protostar.starknet.data_transformer import CairoOrPythonData
from tests.conftest import DevnetAccount

from .tokenizer import tokenize
from .transaction_registry import TransactionRegistry

ContractMap = Dict[str, List[str]]

# pylint: disable=too-many-instance-attributes
def to_contract_name(contract_identifier: str) -> str:
    """
    Converts identifier (path/ contract name) into contract name which can be put into protostar.toml
    For example:
        ./src/basic.cairo -> basic
        basic -> basic
    """
    return Path(contract_identifier).stem


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
        multicall_command: MulticallCommand,
        cli_app: CLIApp,
        parser: ArgumentParserFacade,
        transaction_registry: TransactionRegistry,
        monkeypatch: pytest.MonkeyPatch,
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
        account_address: Address,
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
                "account-address": account_address,
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
        self, targets: List[str], last_failed: bool = False, estimate_gas: bool = False
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

    def create_files(
        self, relative_path_str_to_file: Dict[str, Union[str, Path]]
    ) -> None:
        for relative_path_str, file in relative_path_str_to_file.items():
            if isinstance(file, Path):
                content = file.read_text("utf-8")
            else:
                content = file
            self._save_file(self._project_root_path / relative_path_str, content)

    def create_contracts(self, contract_name_to_file: Dict[str, Path]):
        relative_path_str_to_file = {
            f"src/{contract_name}.cairo": file
            for contract_name, file in contract_name_to_file.items()
        }
        self.create_files(relative_path_str_to_file)
        self.add_contracts_to_protostar_toml(contract_name_to_file)

    def add_contracts_to_protostar_toml(
        self,
        contract_name_to_file: Dict[str, Path],
    ):
        protostar_toml_path = self.project_root_path / "protostar.toml"
        assert (
            protostar_toml_path.is_file()
        ), "No protostar.toml found, cannot change contents."

        interpreter = ConfigurationTOMLInterpreter(
            protostar_toml_path.read_text("utf-8")
        )
        config_file_v2 = ConfigurationFileV2(
            project_root_path=self.project_root_path,
            configuration_file_interpreter=interpreter,
            file_path=protostar_toml_path,
            active_profile_name=None,
        )

        previous_contract_map = {
            contract_name: [
                str(src_path)
                for src_path in config_file_v2.get_contract_source_paths(contract_name)
            ]
            for contract_name in config_file_v2.get_contract_names()
        }

        new_contract_map = {
            contract_name: [str(file_path.resolve())]
            for contract_name, file_path in contract_name_to_file.items()
        }

        overriden_config_file_model_v2 = ConfigurationFileV2Model(
            protostar_version=config_file_v2.get_declared_protostar_version(),
            contract_name_to_path_strs={
                **previous_contract_map,
                **new_contract_map,
            },
            project_config={},
            command_name_to_config={},
            profile_name_to_project_config={},
            profile_name_to_commands_config={},
        )
        content_factory = ConfigurationFileV2ContentFactory(
            content_builder=ConfigurationTOMLContentBuilder()
        )
        file_content = content_factory.create_file_content(
            overriden_config_file_model_v2
        )
        protostar_toml_path.write_text(file_content)

    async def run_test_runner(
        self, target: Union[str, Path], cairo_test_runner: bool = False
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
            use_cairo_test_runner=cairo_test_runner,
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

    @staticmethod
    def _save_file(path: Path, content: str) -> None:
        path.parent.mkdir(exist_ok=True, parents=True)
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(content)
