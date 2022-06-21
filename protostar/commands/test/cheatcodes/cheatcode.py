# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
from abc import abstractmethod
import inspect
from typing import TYPE_CHECKING, Any, Type, cast
from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)

from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.commands.test.starkware.cheatable_carried_state import (
    CheatableCarriedState,
)
from protostar.commands.test.starkware.cheatable_starknet_general_config import (
    CheatableStarknetGeneralConfig,
)

if TYPE_CHECKING:
    from protostar.commands.test.starkware.cheatable_execute_entry_point import (
        CheatableExecuteEntryPoint,
    )


class Cheatcode(BusinessLogicSysCallHandler):
    def __init__(
        self,
        execute_entry_point_cls: Type["CheatableExecuteEntryPoint"],
        tx_execution_context: TransactionExecutionContext,
        state: CheatableCarriedState,
        caller_address: int,
        contract_address: int,
        starknet_storage: BusinessLogicStarknetStorage,
        general_config: CheatableStarknetGeneralConfig,
        initial_syscall_ptr: RelocatableValue,
    ):
        super().__init__(
            execute_entry_point_cls,
            tx_execution_context,
            state,
            caller_address,
            contract_address,
            starknet_storage,
            general_config,
            initial_syscall_ptr,
        )
        self.state = state
        self.general_config = general_config
        self.execute_entry_point_cls = execute_entry_point_cls

    @staticmethod
    @abstractmethod
    def name() -> str:
        ...

    @staticmethod
    @abstractmethod
    def implementation() -> str:
        ...


class CheatcodeFactory:
    def __init__(
        self,
        execute_entry_point_cls: Type["CheatableExecuteEntryPoint"],
        tx_execution_context: TransactionExecutionContext,
        state: CheatableCarriedState,
        caller_address: int,
        contract_address: int,
        starknet_storage: BusinessLogicStarknetStorage,
        general_config: CheatableStarknetGeneralConfig,
        initial_syscall_ptr: RelocatableValue,
    ):
        self.execute_entry_point_cls = execute_entry_point_cls
        self.tx_execution_context = tx_execution_context
        self.state = state
        self.caller_address = caller_address
        self.contract_address = contract_address
        self.starknet_storage = starknet_storage
        self.general_config = general_config
        self.initial_syscall_ptr = initial_syscall_ptr

    def build(self, cheatcode_type: Type[Cheatcode]):
        cheatcode_args_types = inspect.signature(cheatcode_type).parameters
        cheatcode_args = [getattr(self, name) for name in cheatcode_args_types]
        return cheatcode_type(*cheatcode_args)
