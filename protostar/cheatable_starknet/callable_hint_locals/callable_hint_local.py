from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Union, Optional

from starkware.cairo.lang.compiler.test_utils import short_string_to_felt

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.controllers.transaction_revert_exception import (
    TransactionRevertException,
)


@dataclass(frozen=True)
class InvalidExecution:
    ok = None
    panic_data: Optional[list[int]] = None
    err_code: Optional[int] = None


@dataclass(frozen=True)
class ValidExecution:
    ok: Any
    panic_data = None
    err_code = 0


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
            # TODO: Come up with an exception for non-execution-based cheatcodes, wrap and catch them
            except Exception as exc:
                return InvalidExecution(
                    panic_data=None, err_code=short_string_to_felt(str(exc)[:31])
                )

        return wrapper
