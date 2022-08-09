from typing import Optional

from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzConfig,
    FuzzTestExecutionEnvironment,
    is_fuzz_test,
)
from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_case_runners.fuzz_test_case_runner import (
    FuzzTestCaseRunner,
)
from protostar.commands.test.test_case_runners.standard_test_case_runner import (
    StandardTestCaseRunner,
)
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner
from protostar.commands.test.test_suite import TestSuite


class TestCaseRunnerFactory:
    def __init__(self, state: TestExecutionState, test_suite: TestSuite) -> None:
        self._state = state
        self._test_suite = test_suite

    def make(
        self, test_case_name: str, fuzz_config: Optional[FuzzConfig] = None
    ) -> TestCaseRunner:
        state = self._state.fork()
        if is_fuzz_test(test_case_name, state):
            return self._make_fuzz_test_case_runner(state, fuzz_config)
        return self._make_standard_test_case_runner(state)

    def _make_standard_test_case_runner(
        self, state: TestExecutionState
    ) -> StandardTestCaseRunner:
        env = TestExecutionEnvironment(state)
        return StandardTestCaseRunner(
            env,
            dependencies=TestCaseRunner.Dependencies(
                test_suite=self._test_suite, output_recorder=state.output_recorder
            ),
        )

    def _make_fuzz_test_case_runner(
        self, state: TestExecutionState, fuzz_config: Optional[FuzzConfig] = None
    ) -> FuzzTestCaseRunner:
        env = FuzzTestExecutionEnvironment(state, fuzz_config=fuzz_config)
        return FuzzTestCaseRunner(
            env,
            dependencies=TestCaseRunner.Dependencies(
                test_suite=self._test_suite, output_recorder=state.output_recorder
            ),
        )
