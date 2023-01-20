from typing import cast

from starkware.cairo.lang.compiler.program import Program

from protostar.cairo import HintLocalsDict
from protostar.cairo_testing.execution_environments.cairo_execution_environment import (
    CairoExecutionEnvironment,
)
from protostar.cairo_testing.cairo_test_execution_state import CairoTestExecutionState
from protostar.cairo_testing.cheatcode_factories.cairo_setup_cheatcode_factory import (
    CairoSetupCheatcodeFactory,
)
from protostar.cheatable_starknet.cheatable_cached_state import CheatableCachedState
from protostar.testing.test_context import TestContextHintLocal


class CairoSetupExecutionEnvironment(CairoExecutionEnvironment):
    def __init__(
        self,
        program: Program,
        state: CairoTestExecutionState,
    ):
        super().__init__(state, program, self._get_hint_locals(state))

    async def execute(self, function_name: str):
        with self.state.output_recorder.redirect("setup"):
            await self.run_cairo_function(function_name)

    def _get_hint_locals(self, state: CairoTestExecutionState) -> HintLocalsDict:
        hint_locals: HintLocalsDict = {}
        cheatcode_factory = CairoSetupCheatcodeFactory(
            cheatable_state=cast(CheatableCachedState, state.starknet.state.state),
            project_compiler=state.project_compiler,
        )
        cheatcodes = cheatcode_factory.build_cheatcodes()
        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

        custom_hint_locals = [TestContextHintLocal(state.context)]

        for custom_hint_local in custom_hint_locals:
            hint_locals[custom_hint_local.name] = custom_hint_local.build()

        return hint_locals
