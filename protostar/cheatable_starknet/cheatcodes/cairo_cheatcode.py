from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Union

from typing_extensions import Literal
from starknet_py.cairo.felt import encode_shortstring

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.cheaters.transaction_revert_exception import (
    TransactionRevertException,
)

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheaters import CairoCheaters

Felt = int


@dataclass(init=False)
class CairoCheatcodeInvalidExecution:
    ok = None
    err_code: int

    def __init__(self, err_code: int):
        assert err_code > 0
        self.err_code = err_code


@dataclass(frozen=True)
class CairoCheatcodeValidExecution:
    ok: Any
    err: Literal[0] = 0


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
            except TransactionRevertException as ex:
                return CairoCheatcodeInvalidExecution(
                    err_code=encode_shortstring(ex.message)
                )

        return wrapper
