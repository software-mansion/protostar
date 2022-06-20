from collections.abc import Mapping
from typing import Dict, List, Type, Union

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.execute_entry_point_base import (
    ExecuteEntryPointBase,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.commands.test.starkware.cheatable_carried_state import (
    CheatableCarriedState,
)
from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)
from protostar.commands.test.starkware.cheatable_syscall_handler import (
    CheatableSysCallHandler,
)
from protostar.utils.data_transformer_facade import DataTransformerFacade
from protostar.utils.starknet_compilation import StarknetCompiler


class MockCallMisusageException(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MockCallCheatcode(CheatableSysCallHandler):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        execute_entry_point_cls: Type[ExecuteEntryPointBase],
        tx_execution_context: TransactionExecutionContext,
        state: CheatableCarriedState,
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
            contract_path = self.get_contract_path_from_contract_address(
                contract_address
            )
            if contract_path is None:
                raise MockCallMisusageException(
                    (
                        "Couldn't map the `contract_address` to the contract path."
                        "Is the `contract_address` valid?"
                    ),
                )

            ret_data = self.data_transformer_facade.build_from_python_transformer(
                contract_path, fn_name, "outputs"
            )(ret_data)

        if selector in self.cheatable_state.mocked_calls_map[contract_address]:
            raise MockCallMisusageException(
                f"{selector} in contract with address {contract_address} has been already mocked"
            )
        self.cheatable_state.mocked_calls_map[contract_address][selector] = ret_data

        def clear_mock():
            if contract_address not in self.cheatable_state.mocked_calls_map:
                raise MockCallMisusageException(
                    f"Contract {contract_address} doesn't have mocked selectors."
                )
            if selector not in self.cheatable_state.mocked_calls_map[contract_address]:
                raise MockCallMisusageException(
                    f"Couldn't find mocked selector {selector} for an address {contract_address}."
                )
            del self.cheatable_state.mocked_calls_map[contract_address][selector]

        return clear_mock
