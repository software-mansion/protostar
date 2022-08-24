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
            return FuzzTestCaseRunner(
                fuzz_test_execution_environment=FuzzTestExecutionEnvironment(state),
                test_case=test_case,
                output_recorder=state.output_recorder,
            )

        if state.config.mode is TestMode.STANDARD:
            return StandardTestCaseRunner(
                test_execution_environment=TestExecutionEnvironment(state),
                test_case=test_case,
                output_recorder=state.output_recorder,
            )

        raise NotImplementedError(f"Unreachable")
