from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
    TestExecutionResult,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner


class StandardTestCaseRunner(TestCaseRunner[TestExecutionResult]):
    def __init__(
        self, test_execution_environment: TestExecutionEnvironment, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._test_execution_environment = test_execution_environment

    async def _run_test_case(self) -> TestExecutionResult:
        return await self._test_execution_environment.invoke(
            self.test_case.test_fn_name
        )
