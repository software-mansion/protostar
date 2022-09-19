from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
    TestExecutionResult,
)


class StandardTestExecutionEnvironment(TestExecutionEnvironment):
    async def execute(self, function_name: str, profile=False) -> TestExecutionResult:
        self.set_profile_flag(profile)
        return await super().execute(function_name)
