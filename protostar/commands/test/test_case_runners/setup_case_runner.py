from protostar.commands.test.environments.setup_case_execution_environment import (
    SetupCaseExecutionEnvironment,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_results import (
    SetupCaseResult,
    PassedSetupCaseResult,
    FailedSetupCaseResult,
)
from protostar.commands.test.test_suite import TestCase


async def run_setup_case(
    test_case: TestCase, state: TestExecutionState
) -> SetupCaseResult:
    assert test_case.setup_fn_name

    try:
        execution_environment = SetupCaseExecutionEnvironment(state)

        with state.stopwatch.lap(test_case.setup_fn_name):
            await execution_environment.invoke(test_case.setup_fn_name)

        return PassedSetupCaseResult(
            file_path=test_case.test_path,
            test_case_name=test_case.test_fn_name,
            setup_case_name=test_case.setup_fn_name,
            execution_time=state.stopwatch.total_elapsed,
        )
    except ReportedException as ex:
        return FailedSetupCaseResult(
            file_path=test_case.test_path,
            test_case_name=test_case.test_fn_name,
            setup_case_name=test_case.setup_fn_name,
            exception=ex,
            execution_time=state.stopwatch.total_elapsed,
            captured_stdout=state.output_recorder.get_captures(),
        )
