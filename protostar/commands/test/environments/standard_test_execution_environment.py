from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
    TestExecutionResult,
)


class StandardTestExecutionEnvironment(TestExecutionEnvironment):
    def __init__(self, *args, profiling=False, **kwargs):
        self.profiling = profiling
        super().__init__(*args, **kwargs)

    async def execute(self, function_name: str) -> TestExecutionResult:
        self.set_profile_flag(self.profiling)
        return await super().execute(function_name)
