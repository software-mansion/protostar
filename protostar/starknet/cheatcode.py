from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Type

from starkware.cairo.lang.vm.relocatable import RelocatableValue
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionContext,
)
from starkware.starknet.core.os.syscall_utils import BusinessLogicSysCallHandler
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import AbiType
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage
from starkware.starknet.testing.contract_utils import EventManager
from typing_extensions import TypedDict

from protostar.starknet.hint_local import HintLocal

if TYPE_CHECKING:
    from protostar.starknet.cheatable_execute_entry_point import (
        CheatableExecuteEntryPoint,
    )
    from protostar.starknet.cheatable_state import CheatableCarriedState


class Cheatcode(BusinessLogicSysCallHandler, HintLocal):
    class SyscallDependencies(TypedDict):
        execute_entry_point_cls: Type["CheatableExecuteEntryPoint"]
        tx_execution_context: TransactionExecutionContext
        state: "CheatableCarriedState"
        caller_address: int
        contract_address: int
        starknet_storage: BusinessLogicStarknetStorage
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
        abi = self.state.get_abi_from_contract_address(
            syscall_dependencies["contract_address"]
        )
        self._add_event_abi_to_state(abi)

    @abstractmethod
    def build(self) -> Callable[..., Any]:
        ...

    def _add_event_abi_to_state(self, abi: AbiType):
        event_manager = EventManager(abi=abi)
        self.state.update_event_selector_to_name_map(
            # pylint: disable=protected-access
            event_manager._selector_to_name
        )
        # pylint: disable=protected-access
        for event_name in event_manager._selector_to_name.values():
            self.state.event_name_to_contract_abi_map[event_name] = abi
