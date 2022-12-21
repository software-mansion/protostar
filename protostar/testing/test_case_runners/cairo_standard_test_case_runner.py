from typing import Any

from starkware.cairo.lang.compiler.program import Program

from protostar.testing.environments.test_execution_environment import (
    TestExecutionResult,
    TestExecutionEnvironment,
)
from .standard_test_case_runner import StandardTestCaseRunner


class CairoStandardTestCaseRunner(StandardTestCaseRunner):
    def __init__(
        self,
        program: Program,
        test_execution_environment: TestExecutionEnvironment,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._program = program
        self._test_execution_environment = test_execution_environment

    async def _run_test_case(self) -> TestExecutionResult:
        return await self._test_execution_environment.execute(
            self._test_case.test_fn_name
        )
