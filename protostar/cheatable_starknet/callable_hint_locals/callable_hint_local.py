from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Union

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.controllers.transaction_revert_exception import (
    TransactionRevertException,
)


@dataclass(frozen=True)
class InvalidExecution:
    ok = None
    panic_data: list[int]


@dataclass(frozen=True)
class ValidExecution:
    ok: Any
    panic_data = None


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
            except TransactionRevertException as ex:
                return InvalidExecution(panic_data=ex.get_panic_data())

        return wrapper
