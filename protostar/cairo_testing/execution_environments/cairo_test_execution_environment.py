from typing import Any

from starkware.cairo.lang.compiler.program import Program

from protostar.testing.environments.execution_environment import (
    TestExecutionResult,
)

from protostar.testing.cheatcodes.expect_revert_cheatcode import ExpectRevertContext
from protostar.testing.hook import Hook
from protostar.testing.test_context import TestContextHintLocal
from protostar.cairo_testing.cairo_test_execution_state import CairoTestExecutionState
from protostar.cairo_testing.cheatcode_factories.cairo_test_cheatcode_factory import (
    CairoTestCheatcodeFactory,
)
from protostar.cairo import HintLocalsDict

from protostar.cheatable_starknet.cheatable_cached_state import CheatableCachedState
from protostar.cheatable_starknet.cheaters.expects import ExpectsCairoCheater
from protostar.protostar_exception import ProtostarException
from protostar.cheatable_starknet.cheaters.expects import ExpectsCheaterException
from protostar.starknet import ReportedException

from .cairo_execution_environment import CairoExecutionEnvironment


class CairoTestExecutionEnvironment(CairoExecutionEnvironment):
    def __init__(
        self,
        state: CairoTestExecutionState,
        program: Program,
    ):
        super().__init__(
            state=state, program=program, hint_locals=self._get_hint_locals(state)
        )
        self._expect_revert_context = ExpectRevertContext()
        self._finish_hook = Hook()

    async def execute(self, function_name: str) -> Any:
        with self.state.output_recorder.redirect("test"):
            result = TestExecutionResult(
                execution_resources=await self.execute_test_case(function_name)
            )
            try:
                cheatable_state = self.state.starknet.state.state
                assert isinstance(cheatable_state, CheatableCachedState)
                ExpectsCairoCheater.assert_no_expected_calls(
                    cheatable_state.expected_contract_calls
                )
            except (ProtostarException, ExpectsCheaterException) as e:
                raise ReportedException from e
            return result

    # TODO #1303: Estimate gas if self.state.config.gas_estimation_enabled
    async def execute_test_case(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        async with self._expect_revert_context.test():
            async with self._finish_hook.run_after():
                await self.run_cairo_function(function_name, *args, **kwargs)

    def _get_hint_locals(self, state: CairoTestExecutionState) -> HintLocalsDict:
        hint_locals: HintLocalsDict = {}
        cheatcode_factory = CairoTestCheatcodeFactory(
            cheatable_state=state.cheatable_state,
            project_compiler=state.project_compiler,
        )
        cheatcodes = cheatcode_factory.build_cheatcodes()
        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

        custom_hint_locals = [TestContextHintLocal(state.context)]

        for custom_hint_local in custom_hint_locals:
            hint_locals[custom_hint_local.name] = custom_hint_local.build()

        return hint_locals
