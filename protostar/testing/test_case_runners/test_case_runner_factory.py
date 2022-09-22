from protostar.testing.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
)
from protostar.testing.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.testing.starkware.test_execution_state import TestExecutionState
from protostar.testing.test_config import TestMode
from protostar.testing.test_suite import TestCase

from .fuzz_test_case_runner import FuzzTestCaseRunner
from .standard_test_case_runner import StandardTestCaseRunner
from .test_case_runner import TestCaseRunner

class TestCaseRunnerFactory:
    def __init__(self, state: TestExecutionState) -> None:
        self._state = state

    def make(self, test_case: TestCase, profiling=False) -> TestCaseRunner:
        mode = self._state.config.mode

        assert mode, "Test mode should be determined at this point."
        if mode is TestMode.FUZZ:
            return FuzzTestCaseRunner(
                fuzz_test_execution_environment=FuzzTestExecutionEnvironment(
                    self._state,
                    profiling=profiling,
                ),
                test_case=test_case,
                output_recorder=self._state.output_recorder,
                stopwatch=self._state.stopwatch,
            )

        if mode is TestMode.STANDARD:
            return StandardTestCaseRunner(
                test_execution_environment=TestExecutionEnvironment(
                    self._state,
                    profiling=profiling,
                ),
                test_case=test_case,
                output_recorder=self._state.output_recorder,
                stopwatch=self._state.stopwatch,
            )

        raise NotImplementedError("Unreachable")
