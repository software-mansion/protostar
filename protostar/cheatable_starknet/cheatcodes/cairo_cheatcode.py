from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Union

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.cheatable_exception import CheatableException

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheaters import CairoCheaters


@dataclass
class CairoCheatcodeInvalidExecution:
    ok = None
    err: CheatableException


@dataclass
class CairoCheatcodeValidExecution:
    ok: Callable
    err = None


CairoCheatcodeExecutionResult = Union[
    CairoCheatcodeValidExecution, CairoCheatcodeInvalidExecution
]


class CairoCheatcode(HintLocal, ABC):
    def __init__(self, cheaters: "CairoCheaters"):
        self.cheaters = cheaters

    @abstractmethod
    def _build(self) -> Callable:
        ...

    def build(self):
        def wrapper(*args: Any, **kwargs: Any):
            try:
                result = self._build()(*args, **kwargs)
                return CairoCheatcodeValidExecution(ok=result)
            except CheatableException as ex:
                return CairoCheatcodeInvalidExecution(err=ex)

        return wrapper
