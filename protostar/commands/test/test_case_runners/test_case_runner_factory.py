from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_case_runners.test_case_runner import TestCaseRunner
from protostar.commands.test.test_suite import TestCase


# TODO(mkaput): Remove this class in favor of forking state directly in TestRunner.
#   In the past this class did more, but now it has been stripped off.
class TestCaseRunnerFactory:
    def __init__(self, state: TestExecutionState) -> None:
        self._state = state

    def make(self, test_case: TestCase) -> TestCaseRunner:
        state: TestExecutionState = self._state.fork()
        return TestCaseRunner(test_case, state)
