from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Type

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from typing_extensions import TypedDict

from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.hint_local import HintLocal

if TYPE_CHECKING:
    from protostar.starknet.cheatable_execute_entry_point import (
        CheatableExecuteEntryPoint,
    )


class Cheatcode(BusinessLogicSysCallHandler, HintLocal):
    class SyscallDependencies(TypedDict):
        execute_entry_point_cls: Type["CheatableExecuteEntryPoint"]
        tx_execution_context: TransactionExecutionContext
        state: SyncState
        resources_manager: ExecutionResourcesManager
        caller_address: int
        contract_address: int
        general_config: StarknetGeneralConfig
        initial_syscall_ptr: RelocatableValue

    def __init__(
        self,
        syscall_dependencies: SyscallDependencies,
    ):
        super().__init__(**syscall_dependencies)

        # assigning properties to preserve "cheatable" types
        self.state = syscall_dependencies["state"]
        self.general_config = syscall_dependencies["general_config"]
        self.execute_entry_point_cls = syscall_dependencies["execute_entry_point_cls"]

    @property
    def cheatable_state(self) -> CheatableCachedState:
        state_syncifier = self.state
        assert isinstance(state_syncifier, StateSyncifier)

        async_state = state_syncifier.async_state
        assert isinstance(async_state, CheatableCachedState)

        return async_state

    @abstractmethod
    def build(self) -> Any:
        ...
