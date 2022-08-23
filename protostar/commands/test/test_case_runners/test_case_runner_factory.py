from protostar.commands.test.environments.fuzz_test_execution_environment import (
    FuzzTestExecutionEnvironment,
)
from protostar.commands.test.environments.test_execution_environment import (
    TestExecutionEnvironment,
)
from protostar.commands.test.fuzzing.fuzz_test_case_result_decorator import (
    FuzzTestCaseResultDecorator,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner
from protostar.commands.test.test_config import TestMode
from protostar.commands.test.test_suite import TestCase


class TestCaseRunnerFactory:
    def __init__(self, state: TestExecutionState) -> None:
        self._state = state

    def make(self, test_case: TestCase) -> TestCaseRunner:
        state: TestExecutionState = self._state.fork()

        # TODO(mkaput): Remove this in favor of setting mode explicitly by cheatcodes in setup hooks.
        state.config.mode = TestMode.infer_from_contract_function(
            test_case.test_fn_name, state.contract
        )

        if state.config.mode is TestMode.FUZZ:
            return TestCaseRunner(
                execution_environment=FuzzTestExecutionEnvironment(state),
                test_case=test_case,
                output_recorder=state.output_recorder,
                test_case_result_decorator=FuzzTestCaseResultDecorator(),
            )

        if state.config.mode is TestMode.STANDARD:
            return TestCaseRunner(
                execution_environment=TestExecutionEnvironment(state),
                test_case=test_case,
                output_recorder=state.output_recorder,
            )

        raise NotImplementedError(f"Unreachable")
