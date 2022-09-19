from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
)
from protostar.commands.test.environments.standard_test_execution_environment import (
    StandardTestExecutionEnvironment,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_case_runners.fuzz_test_case_runner import (
    FuzzTestCaseRunner,
)
from protostar.commands.test.test_case_runners.standard_test_case_runner import (
    StandardTestCaseRunner,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner
from protostar.commands.test.test_config import TestMode
from protostar.commands.test.test_suite import TestCase
from protostar.protostar_exception import ProtostarException


class TestCaseRunnerFactory:
    def __init__(self, state: TestExecutionState) -> None:
        self._state = state

    def make(self, test_case: TestCase, profile=False) -> TestCaseRunner:
        mode = self._state.config.mode

        assert mode, "Test mode should be determined at this point."
        if mode is TestMode.FUZZ and profile:
            raise ProtostarException("You cannot profile fuzz tests")

        if mode is TestMode.FUZZ:
            return FuzzTestCaseRunner(
                fuzz_test_execution_environment=FuzzTestExecutionEnvironment(
                    self._state
                ),
                test_case=test_case,
                output_recorder=self._state.output_recorder,
                stopwatch=self._state.stopwatch,
            )

        if mode is TestMode.STANDARD:
            return StandardTestCaseRunner(
                test_execution_environment=StandardTestExecutionEnvironment(
                    self._state, profile=profile
                ),
                test_case=test_case,
                output_recorder=self._state.output_recorder,
                stopwatch=self._state.stopwatch,
            )

        raise NotImplementedError("Unreachable")
