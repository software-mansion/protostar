from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Union

from typing_extensions import Literal
from starknet_py.cairo.felt import encode_shortstring

from protostar.cairo import HintLocal


@dataclass(init=False)
class InvalidExecution:
    ok = None
    err_code: int

    def __init__(self, err_code: int):
        assert (
            err_code > 0
        ), "Error code 0 is reserved for successful execution. Error code must be a positive number."
        self.err_code = err_code


@dataclass(frozen=True)
class ValidExecution:
    ok: Any
    err_code: Literal[0] = 0


ExecutionResult = Union[ValidExecution, InvalidExecution]


class CallableHintLocal(HintLocal, ABC):
    @abstractmethod
    def _build(self) -> Callable:
        ...

    def build(self):
        def wrapper(*args: Any, **kwargs: Any) -> ExecutionResult:
            try:
                result = self._build()(*args, **kwargs)
                return ValidExecution(ok=result)
            except BaseException as ex:
                return InvalidExecution(err_code=encode_shortstring(str(ex)[:31]))

        return wrapper
