from abc import ABC, abstractmethod
from typing import List

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.hint_local import HintLocal


class CheatcodeFactory(ABC):
    @abstractmethod
    def build_cheatcodes(
        self, syscall_dependencies: Cheatcode.SyscallDependencies
    ) -> List[Cheatcode]:
        ...

    @abstractmethod
    def build_hint_locals(self) -> List[HintLocal]:
        ...
