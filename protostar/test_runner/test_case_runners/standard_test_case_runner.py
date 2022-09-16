from protostar.test_runner.environments.test_execution_environment import (
    TestExecutionEnvironment,
    TestExecutionResult,
)

from .test_case_runner import TestCaseRunner


class StandardTestCaseRunner(TestCaseRunner[TestExecutionResult]):
    def __init__(
        self, test_execution_environment: TestExecutionEnvironment, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._test_execution_environment = test_execution_environment

    async def _run_test_case(self) -> TestExecutionResult:
        return await self._test_execution_environment.execute(
            self._test_case.test_fn_name
        )
