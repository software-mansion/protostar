import asyncio
from typing import Any, Optional

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.vm_exceptions import VmException

from protostar.testing.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.testing.test_environment_exceptions import RevertableException

from .cairo_test_cheatcode_factory import (
    CairoTestCheatcodeFactory,
)
from .cairo_test_execution_state import CairoTestExecutionState
from ..cheatcodes.expect_revert_cheatcode import ExpectRevertContext
from ..environments.execution_environment import (
    ExecutionEnvironment,
    TestExecutionResult,
)
from ..hook import Hook


class CairoTestExecutionEnvironment(ExecutionEnvironment):
    state: CairoTestExecutionState

    def __init__(self, program: Program, state: CairoTestExecutionState):
        super().__init__(state)
        self._program = program
        self._max_steps = self.state.config.max_steps
        self._expect_revert_context = ExpectRevertContext()
        self._finish_hook = Hook()
        self._profiling = self.state.config.profiling

    async def execute(self, function_name: str) -> TestExecutionResult:
        with self.state.output_recorder.redirect("test"):
            return TestExecutionResult(
                execution_resources=await self.execute_test_case(function_name)
            )

    # TODO #1303: Estimate gas if self.state.config.gas_estimation_enabled
    async def execute_test_case(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[ExecutionResourcesSummary]:
        async with self._expect_revert_context.test():
            async with self._finish_hook.run_after():
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(
                    executor=None,
                    func=lambda: self.run_cairo_function(
                        function_name, *args, **kwargs
                    ),
                )

    def run_cairo_function(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ):
        try:
            hint_locals = self._get_hint_locals()
            runner = CairoFunctionRunner(program=self._program, layout="all")
            runner.run(function_name, *args, hint_locals=hint_locals, **kwargs)
        except VmException as vm_ex:
            error_message = vm_ex.message
            if hasattr(vm_ex.inner_exc, "exception_str"):
                error_message += vm_ex.inner_exc.exception_str

            raise RevertableException(error_message) from vm_ex

    def _get_hint_locals(self) -> dict[str, Any]:
        hint_locals: dict[str, Any] = {}
        cheatcode_factory = CairoTestCheatcodeFactory(
            state=self.state,
        )
        cheatcodes = cheatcode_factory.build_cheatcodes()
        for cheatcode in cheatcodes:
            hint_locals[cheatcode.name] = cheatcode.build()

        return hint_locals
