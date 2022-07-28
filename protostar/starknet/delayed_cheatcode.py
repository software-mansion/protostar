from typing import Dict, Callable, Any
from abc import abstractmethod
from protostar.starknet.cheatcode import Cheatcode


class DelayedCheatcode(Cheatcode):
    @abstractmethod
    def build(self) -> DelayedCallable[]:
        ...

    @abstractmethod
    def internal_build(self, exec_locals: Dict) -> Callable[..., Any]:
        ...


