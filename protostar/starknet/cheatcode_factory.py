from abc import ABC, abstractmethod
from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.starknet.cheatcode import Cheatcode


class CheatcodeFactory(ABC):
    @abstractmethod
    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        ...
