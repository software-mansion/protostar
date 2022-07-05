from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.utils.data_transformer_facade import DataTransformerFacade

if TYPE_CHECKING:
    from protostar.commands.test.execution_state import ExecutionState


class CheatcodeFactory(ABC):
    @abstractmethod
    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        ...


class WithExecutionState:
    def __init__(self, state: "ExecutionState"):
        self.state = state


class WithDataTransformer(WithExecutionState):
    def __init__(self, state: "ExecutionState"):
        super().__init__(state)
        self.data_transformer = DataTransformerFacade(state.starknet_compiler)
