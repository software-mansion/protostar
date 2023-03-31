from starkware.cairo.lang.compiler.program import Program

from protostar.cairo import HintLocalsDict
from protostar.cairo_testing.cairo_hint_local_factory import (
    CairoSetupHintLocalFactory,
    CairoSharedHintLocalFactory,
)
from protostar.cairo.cairo_function_executor import OffsetOrName
from protostar.cairo_testing.execution_environments.cairo_execution_environment import (
    CairoExecutionEnvironment,
)
from protostar.cairo_testing.cairo_test_execution_state import CairoTestExecutionState
from protostar.testing import Hook
from protostar.testing.test_context import TestContextHintLocal


class CairoSetupExecutionEnvironment(CairoExecutionEnvironment):
    def __init__(
        self,
        program: Program,
        state: CairoTestExecutionState,
    ):
        self._finish_hook = (
            Hook()
        )  # assigned before super call, because _get_hint_locals uses this hook
        super().__init__(state, program, self._get_hint_locals(state))

    async def execute(self, function_identifier: OffsetOrName):
        with self.state.output_recorder.redirect("setup"):
            async with self._finish_hook.run_after():
                await self.run_cairo_function(function_identifier)

    def _get_hint_locals(self, state: CairoTestExecutionState) -> HintLocalsDict:
        hint_locals: HintLocalsDict = {}

        cheatcode_factory = CairoSetupHintLocalFactory(
            shared_hint_local_factory=CairoSharedHintLocalFactory(
                cheatable_state=state.cheatable_state,
                cairo0_project_compiler=state.cairo0_project_compiler,
                project_compiler=state.project_compiler,
                test_finish_hook=self._finish_hook,
                test_execution_state=state,
            )
        )
        setup_hint_locals = cheatcode_factory.build_hint_locals()
        for hint_local in setup_hint_locals:
            hint_locals[hint_local.name] = hint_local.build()

        custom_hint_locals = [TestContextHintLocal(state.context)]

        for custom_hint_local in custom_hint_locals:
            hint_locals[custom_hint_local.name] = custom_hint_local.build()

        return hint_locals
