from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Type

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    TransactionExecutionContext,
)
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.business_logic.state.state_api import SyncState
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from typing_extensions import TypedDict

from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.cheaters import Cheaters
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
        shared_internal_calls: list[CallInfo]

    def __init__(
        self,
        syscall_dependencies: SyscallDependencies,
    ):
        super().__init__(
            execute_entry_point_cls=syscall_dependencies["execute_entry_point_cls"],
            tx_execution_context=syscall_dependencies["tx_execution_context"],
            state=syscall_dependencies["state"],
            resources_manager=syscall_dependencies["resources_manager"],
            caller_address=syscall_dependencies["caller_address"],
            contract_address=syscall_dependencies["contract_address"],
            general_config=syscall_dependencies["general_config"],
            initial_syscall_ptr=syscall_dependencies["initial_syscall_ptr"],
        )
        self.internal_calls = syscall_dependencies["shared_internal_calls"]

        # assigning properties to preserve "cheatable" types
        self.state: SyncState = syscall_dependencies["state"]
        self.general_config: StarknetGeneralConfig = syscall_dependencies[
            "general_config"
        ]
        self.execute_entry_point_cls: Type[
            "CheatableExecuteEntryPoint"
        ] = syscall_dependencies["execute_entry_point_cls"]

    # TODO(mkaput): Eradicate this property in favor of `cheaters`.
    @property
    def cheatable_state(self) -> CheatableCachedState:
        state_syncifier = self.state
        assert isinstance(state_syncifier, StateSyncifier)

        async_state = state_syncifier.async_state
        assert isinstance(async_state, CheatableCachedState)

        return async_state

    @property
    def cheaters(self) -> Cheaters:
        return self.cheatable_state.cheaters

    @abstractmethod
    def build(self) -> Any:
        ...
