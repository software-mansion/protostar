from typing import Type

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.execute_entry_point_base import (
    ExecuteEntryPointBase,
)
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
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

    def run(self):
        pass
