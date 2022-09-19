from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionResult,
)
from protostar.commands.test.environments.standard_test_execution_environment import (
    StandardTestExecutionEnvironment,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner


class StandardTestCaseRunner(TestCaseRunner[TestExecutionResult]):
    def __init__(
        self, test_execution_environment: StandardTestExecutionEnvironment, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._test_execution_environment = test_execution_environment

    async def _run_test_case(self) -> TestExecutionResult:
        return await self._test_execution_environment.execute(
            self._test_case.test_fn_name
        )
