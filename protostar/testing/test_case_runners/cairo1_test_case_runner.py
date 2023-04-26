from typing import TypeVar, Any

from protostar.cairo.cairo_function_executor import CairoFunctionExecutor
from protostar.testing.test_case_runners.test_case_runner import TestCaseRunner
from protostar.testing.test_suite import Cairo1TestCase

T = TypeVar("T")


class Cairo1TestCaseRunner(TestCaseRunner[T]):
    def __init__(
        self,
        function_executor: CairoFunctionExecutor[T],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._function_executor = function_executor

    async def _run_test_case(self) -> T:
        assert isinstance(
            self._test_case, Cairo1TestCase
        ), "Cairo 1 runner is not capable of running test case without offsets!"
        return await self._function_executor.execute(self._test_case.test_fn_offset)
