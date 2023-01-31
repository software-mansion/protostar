from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Union

from typing_extensions import Literal
from starknet_py.cairo.felt import encode_shortstring

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.controllers.transaction_revert_exception import (
    TransactionRevertException,
)

if TYPE_CHECKING:
    from protostar.cheatable_starknet.controllers import Controllers


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
    def __init__(self, controllers: "Controllers"):
        self.controllers = controllers

    @abstractmethod
    def _build(self) -> Callable:
        ...

    def build(self):
        def wrapper(*args: Any, **kwargs: Any):
            try:
                result = self._build()(*args, **kwargs)
                return ValidExecution(ok=result)
            except TransactionRevertException as ex:
                return InvalidExecution(err_code=encode_shortstring(ex.message))

        return wrapper
