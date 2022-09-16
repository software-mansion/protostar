from protostar.commands.test.environments.setup_case_execution_environment import (
    SetupCaseExecutionEnvironment,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.test_runner.cheatcodes.skip_cheatcode import TestSkipped
from protostar.test_runner.test_results import (
    BrokenSetupCaseResult,
    PassedSetupCaseResult,
    SetupCaseResult,
    SkippedSetupCaseResult,
)
from protostar.test_runner.test_suite import TestCase


async def run_setup_case(
    test_case: TestCase, state: TestExecutionState
) -> SetupCaseResult:
    assert test_case.setup_fn_name

    try:
        execution_environment = SetupCaseExecutionEnvironment(state)

        with state.stopwatch.lap(test_case.setup_fn_name):
            await execution_environment.execute(test_case.setup_fn_name)

        return PassedSetupCaseResult(
            file_path=test_case.test_path,
            test_case_name=test_case.test_fn_name,
            setup_case_name=test_case.setup_fn_name,
            execution_time=state.stopwatch.total_elapsed,
        )
    except TestSkipped as ex:
        return SkippedSetupCaseResult(
            file_path=test_case.test_path,
            test_case_name=test_case.test_fn_name,
            setup_case_name=test_case.setup_fn_name,
            execution_time=state.stopwatch.total_elapsed,
            captured_stdout=state.output_recorder.get_captures(),
            reason=ex.reason,
        )
    except ReportedException as ex:
        return BrokenSetupCaseResult(
            file_path=test_case.test_path,
            test_case_name=test_case.test_fn_name,
            setup_case_name=test_case.setup_fn_name,
            exception=ex,
            execution_time=state.stopwatch.total_elapsed,
            captured_stdout=state.output_recorder.get_captures(),
        )
