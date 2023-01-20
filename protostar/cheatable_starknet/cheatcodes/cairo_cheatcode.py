from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Union

from starknet_py.cairo.felt import encode_shortstring

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.cheatable_exception import CheatableException

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheaters import CairoCheaters

Felt = int


@dataclass
class CheatcodeException:
    code: Felt
    ex: Exception


@dataclass
class CairoCheatcodeInvalidExecution:
    ok = None
    err: CheatcodeException


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
                return CairoCheatcodeInvalidExecution(
                    err=CheatcodeException(
                        code=encode_shortstring(ex.message), ex=ex.raw_ex
                    )
                )

        return wrapper
