import time
from typing import Dict, Type, Tuple

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
)
from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_config import TestMode
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_results import (
    FailedFuzzTestCaseResult,
    FailedTestCaseResult,
    PassedFuzzTestCaseResult,
    PassedTestCaseResult,
    TestCaseResult,
)
from protostar.commands.test.test_suite import TestCase


TEST_CASE_RESULT_TYPES: Dict[
    TestMode, Tuple[Type[PassedTestCaseResult], Type[FailedTestCaseResult]]
] = {
    TestMode.STANDARD: (PassedTestCaseResult, FailedTestCaseResult),
    TestMode.FUZZ: (PassedFuzzTestCaseResult, FailedFuzzTestCaseResult),
}


class TestCaseRunner:
    def __init__(self, test_case: TestCase, state: TestExecutionState):
        self._test_case = test_case
        self._state = state

        # TODO(mkaput): Remove this in favor of setting mode explicitly by cheatcodes in setup hooks.
        state.config.mode = TestMode.infer_from_contract_function(
            test_case.test_fn_name, state.contract
        )

    async def run(self) -> TestCaseResult:
        timer = Timer()
        try:
            with timer:
                # Note: The execution environment has to be selected as late as possible,
                #   because test mode can be changed in setup hooks.
                execution_environment = self._build_test_execution_environment(
                    self._state
                )

                execution_result = await execution_environment.invoke(
                    self._test_case.test_fn_name
                )

            (passed, _) = TEST_CASE_RESULT_TYPES[self._state.config.mode]
            return passed.from_test_execution_result(
                test_execution_result=execution_result,
                file_path=self._test_case.test_path,
                test_case_name=self._test_case.test_fn_name,
                execution_time=timer.elapsed,
                captured_stdout=self._state.output_recorder.get_captures(),
            )
        except ReportedException as ex:
            (_, failed) = TEST_CASE_RESULT_TYPES[self._state.config.mode]
            return failed.from_reported_exception(
                exception=ex,
                file_path=self._test_case.test_path,
                test_case_name=self._test_case.test_fn_name,
                execution_time=timer.elapsed,
                captured_stdout=self._state.output_recorder.get_captures(),
            )

    @staticmethod
    def _build_test_execution_environment(
        state: TestExecutionState,
    ) -> TestExecutionEnvironment:
        test_mode = state.config.mode

        if test_mode is TestMode.STANDARD:
            return TestExecutionEnvironment(state)

        if test_mode is TestMode.FUZZ:
            return FuzzTestExecutionEnvironment(state)

        raise NotImplementedError("Unreachable.")


class Timer:
    def __init__(self):
        self._start_time = None
        self._end_time = None

    def __enter__(self):
        self._start_time = time.perf_counter()
        self._end_time = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.perf_counter()

    @property
    def elapsed(self) -> float:
        assert self._start_time is not None and self._end_time is not None
        return self._end_time - self._start_time
