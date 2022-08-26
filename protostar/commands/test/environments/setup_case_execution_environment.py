from protostar.commands.test.cheatcodes.reflect.cairo_struct import CairoStructHintLocal
from protostar.commands.test.environments.setup_execution_environment import (
    SetupExecutionEnvironment,
    SetupCheatcodeFactory,
)
from protostar.commands.test.test_context import TestContextHintLocal


class SetupCaseExecutionEnvironment(SetupExecutionEnvironment):
    async def invoke(self, function_name: str):
        self.set_cheatcodes(SetupCaseCheatcodeFactory(self.state))
        self.set_custom_hint_locals(
            [TestContextHintLocal(self.state.context), CairoStructHintLocal()]
        )

        with self.state.output_recorder.redirect("setup case"):
            await self.perform_invoke(function_name)


class SetupCaseCheatcodeFactory(SetupCheatcodeFactory):
    # TODO(mkaput): Extend this in the future.
    pass
