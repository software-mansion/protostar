from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
    TestExecutionResult,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner


class StandardTestCaseRunner(TestCaseRunner[TestExecutionResult]):
    def __init__(
        self,
        test_execution_environment: TestExecutionEnvironment,
        dependencies: TestCaseRunner.Dependencies,
    ) -> None:
        super().__init__(dependencies)
        self._test_execution_environment = test_execution_environment

    async def _run_test_case(self, test_case_name: str) -> TestExecutionResult:
        return await self._test_execution_environment.invoke(test_case_name)
