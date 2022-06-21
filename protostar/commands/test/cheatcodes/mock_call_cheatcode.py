from collections.abc import Mapping
from typing import TYPE_CHECKING, Dict, List, Type, Union

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.execute_entry_point_base import (
    ExecuteEntryPointBase,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.utils.data_transformer_facade import DataTransformerFacade
from protostar.utils.starknet_compilation import StarknetCompiler

if TYPE_CHECKING:
    from protostar.commands.test.starkware.cheatable_state import CheatableCarriedState


class MockCallCheatcode(CheatableSysCallHandler):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        execute_entry_point_cls: Type[ExecuteEntryPointBase],
        tx_execution_context: TransactionExecutionContext,
        state: "CheatableCarriedState",
        caller_address: int,
        contract_address: int,
        starknet_storage: BusinessLogicStarknetStorage,
        general_config: CheatableStarknetGeneralConfig,
        initial_syscall_ptr: RelocatableValue,
    ):
        super().__init__(
            execute_entry_point_cls=execute_entry_point_cls,
            tx_execution_context=tx_execution_context,
            state=state,
            caller_address=caller_address,
            contract_address=contract_address,
            starknet_storage=starknet_storage,
            general_config=general_config,
            initial_syscall_ptr=initial_syscall_ptr,
        )
        self.data_transformer_facade = DataTransformerFacade(
            StarknetCompiler(
                include_paths=general_config.cheatcodes_cairo_path,
                disable_hint_validation=True,
            )
        )

    @property
    def name(self) -> str:
        return "mock_call"

    def execute(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: Union[
            List[int],
            Dict[
                DataTransformerFacade.ArgumentName,
                DataTransformerFacade.SupportedType,
            ],
        ],
    ):
        selector = get_selector_from_name(fn_name)
        if isinstance(ret_data, Mapping):
            ret_data = self._transform_ret_data_to_cairo_format(
                contract_address, fn_name, ret_data
            )

        if contract_address not in self.cheatable_state.mocked_calls_map:
            self.cheatable_state.mocked_calls_map[contract_address] = {}

        if selector in self.cheatable_state.mocked_calls_map[contract_address]:
            raise CheatcodeException(
                self.name,
                f"'{fn_name}' in the contract with address {contract_address} has been already mocked",
            )
        self.cheatable_state.mocked_calls_map[contract_address][selector] = ret_data

        def clear_mock():
            if contract_address not in self.cheatable_state.mocked_calls_map:
                raise CheatcodeException(
                    self.name,
                    f"Contract {contract_address} doesn't have mocked selectors.",
                )
            if selector not in self.cheatable_state.mocked_calls_map[contract_address]:
                raise CheatcodeException(
                    self.name,
                    f"Couldn't find mocked selector {selector} for an address {contract_address}.",
                )
            del self.cheatable_state.mocked_calls_map[contract_address][selector]

        return clear_mock

    def _transform_ret_data_to_cairo_format(
        self,
        contract_address: int,
        fn_name: str,
        ret_data: Dict[
            DataTransformerFacade.ArgumentName,
            DataTransformerFacade.SupportedType,
        ],
    ) -> List[int]:
        contract_path = self.get_contract_path_from_contract_address(contract_address)
        if contract_path is None:
            raise CheatcodeException(
                self.name,
                (
                    "Couldn't map the `contract_address` to the `contract_path`.\n"
                    f"Is the `contract_address` ({contract_address}) valid?\n"
                ),
            )

        return self.data_transformer_facade.build_from_python_transformer(
            contract_path, fn_name, "outputs"
        )(ret_data)
