from typing import Any

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.cairo.lang.compiler.program import Program
from starkware.cairo.lang.vm.vm_exceptions import VmException

from protostar.testing.environments.test_execution_environment import (
    TestExecutionResult,
)
from protostar.starknet import SimpleReportedException

from .test_case_runner import TestCaseRunner


class PureCairoTestCaseRunner(TestCaseRunner[TestExecutionResult]):
    def __init__(self, program: Program, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._program = program

    async def _run_test_case(self) -> TestExecutionResult:
        runner = CairoFunctionRunner(program=self._program, layout="all")
        try:
            runner.run(self._test_case.test_fn_name)
        except VmException as exc:  # TODO: debug traces for clearer output?
            raise SimpleReportedException(exc.message) from exc
        return TestExecutionResult(
            execution_resources=None
        )  # TODO: Return execution resources
