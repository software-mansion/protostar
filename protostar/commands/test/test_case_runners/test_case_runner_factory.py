from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
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
from protostar.commands.test.test_config import TestMode
from protostar.commands.test.test_suite import TestSuite


class TestCaseRunnerFactory:
    def __init__(self, state: TestExecutionState, test_suite: TestSuite) -> None:
        self._state = state
        self._test_suite = test_suite

    def make(self, test_case_name: str) -> TestCaseRunner:
        state: TestExecutionState = self._state.fork()

        # TODO(mkaput): Remove this in favor of setting mode explicitly by cheatcodes in setup hooks.
        state.config.mode = TestMode.infer_from_contract_function(
            test_case_name, state.contract
        )

        if state.config.mode is TestMode.FUZZ:
            return self._make_fuzz_test_case_runner(state)

        if state.config.mode is TestMode.STANDARD:
            return self._make_standard_test_case_runner(state)

        raise NotImplementedError(f"Unreachable")

    def _make_standard_test_case_runner(
        self, state: TestExecutionState
    ) -> StandardTestCaseRunner:
        return StandardTestCaseRunner(
            TestExecutionEnvironment(state),
            test_case_runner_deps=self._build_test_case_runner_deps(state),
        )

    def _make_fuzz_test_case_runner(
        self, state: TestExecutionState
    ) -> FuzzTestCaseRunner:
        return FuzzTestCaseRunner(
            FuzzTestExecutionEnvironment(state),
            test_case_runner_deps=self._build_test_case_runner_deps(state),
        )

    def _build_test_case_runner_deps(
        self, state: TestExecutionState
    ) -> TestCaseRunner.Dependencies:
        return TestCaseRunner.Dependencies(
            test_suite=self._test_suite, output_recorder=state.output_recorder
        )
