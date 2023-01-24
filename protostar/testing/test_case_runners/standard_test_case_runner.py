from typing import Any, TypeVar

from protostar.cairo.cairo_function_executor import CairoFunctionExecutor
from .test_case_runner import TestCaseRunner

T = TypeVar("T")


class StandardTestCaseRunner(TestCaseRunner[T]):
    def __init__(
        self,
        function_executor: CairoFunctionExecutor[T],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._function_executor = function_executor

    async def _run_test_case(self) -> T:
        return await self._function_executor.execute(self._test_case.test_fn_name)
