from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Union

from starknet_py.cairo.felt import encode_shortstring

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.cheaters.cheater_exception import CheaterException

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheaters import CairoCheaters

Felt = int


@dataclass
class CheatcodeException(Exception):
    code: Felt
    ex: Exception


@dataclass
class CairoCheatcodeInvalidExecution:
    ok = None
    err: CheatcodeException

    def unwrap(self) -> Any:
        raise self.err


@dataclass
class CairoCheatcodeValidExecution:
    ok: Any
    err = None

    def unwrap(self) -> Any:
        return self.ok


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
            except CheaterException as ex:
                return CairoCheatcodeInvalidExecution(
                    err=CheatcodeException(
                        code=encode_shortstring(ex.message), ex=ex.raw_ex
                    )
                )

        return wrapper
