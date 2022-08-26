from abc import ABC, abstractmethod
from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.hint_local import HintLocal


class CheatcodeFactory(ABC):
    @abstractmethod
    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        ...

    @abstractmethod
    def build_hint_locals(self) -> List[HintLocal]:
        ...
