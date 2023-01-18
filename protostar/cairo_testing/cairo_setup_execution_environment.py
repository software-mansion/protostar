import asyncio

from protostar.cairo_testing.cairo_test_execution_environment import (
    CairoTestExecutionEnvironment,
)


class CairoSetupExecutionEnvironment(CairoTestExecutionEnvironment):
    async def execute(self, function_name: str):
        with self.state.output_recorder.redirect("setup"):
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                executor=None,
                func=lambda: self.run_cairo_function(function_name),
            )
