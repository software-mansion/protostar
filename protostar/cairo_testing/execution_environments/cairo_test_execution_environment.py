from typing import Any

from starkware.cairo.lang.compiler.program import Program

from protostar.testing.environments.execution_environment import TestExecutionResult
from protostar.testing.cheatcodes.expect_revert_cheatcode import ExpectRevertContext
from protostar.testing.hook import Hook
from protostar.testing.test_context import TestContextHintLocal
from protostar.cairo_testing.cairo_test_execution_state import CairoTestExecutionState
from protostar.cairo import HintLocalsDict
from protostar.cairo.cairo_function_executor import OffsetOrName

from .cairo_execution_environment import CairoExecutionEnvironment
from ..cairo_hint_local_factory import (
    CairoTestHintLocalFactory,
    CairoSharedHintLocalFactory,
)


class CairoTestExecutionEnvironment(CairoExecutionEnvironment):
    def __init__(
        self,
        state: CairoTestExecutionState,
        program: Program,
    ):
        self._finish_hook = (
            Hook()
        )  # assigned before super call, because _get_hint_locals uses this hook
        super().__init__(
            state=state, program=program, hint_locals=self._get_hint_locals(state)
        )
        self._expect_revert_context = ExpectRevertContext()

    async def execute(self, function_identifier: OffsetOrName) -> Any:
        with self.state.output_recorder.redirect("test"):
            await self.execute_test_case(function_identifier)
            return TestExecutionResult(execution_resources=None)

    async def execute_test_case(
        self,
        function_identifier: OffsetOrName,
        *args: Any,
        **kwargs: Any,
    ):
        async with self._expect_revert_context.test():
            async with self._finish_hook.run_after():
                await self.run_cairo_function(function_identifier, *args, **kwargs)

    def _get_hint_locals(self, state: CairoTestExecutionState) -> HintLocalsDict:
        hint_locals: HintLocalsDict = {}
        cheatcode_factory = CairoTestHintLocalFactory(
            shared_hint_local_factory=CairoSharedHintLocalFactory(
                cheatable_state=state.cheatable_state,
                cairo0_project_compiler=state.cairo0_project_compiler,
                contract_path_resolver=state.contract_path_resolver,
                test_execution_state=state,
                test_finish_hook=self._finish_hook,
            )
        )
        test_hint_locals = cheatcode_factory.build_hint_locals()
        for hint_local in test_hint_locals:
            hint_locals[hint_local.name] = hint_local.build()

        custom_hint_locals = [TestContextHintLocal(state.context)]

        for custom_hint_local in custom_hint_locals:
            hint_locals[custom_hint_local.name] = custom_hint_local.build()

        return hint_locals
