from typing import Any

from .test_case_runner import TestCaseRunner
from ..environments.execution_environment import (
    ExecutionEnvironment,
    TestExecutionResult,
)


class StandardTestCaseRunner(TestCaseRunner[TestExecutionResult]):
    def __init__(
        self,
        test_execution_environment: ExecutionEnvironment,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._test_execution_environment = test_execution_environment

    async def _run_test_case(self) -> TestExecutionResult:
        return await self._test_execution_environment.execute(
            self._test_case.test_fn_name
        )
