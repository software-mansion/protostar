from protostar.compiler import ProjectCompiler
from protostar.testing.cheatcodes.skip_cheatcode import TestSkipped
from protostar.testing.environments.setup_case_execution_environment import (
    SetupCaseExecutionEnvironment,
)
from protostar.testing.starkware.test_execution_state import TestExecutionState
from protostar.testing.test_environment_exceptions import ReportedException
from protostar.testing.test_results import (
    BrokenSetupCaseResult,
    PassedSetupCaseResult,
    SetupCaseResult,
    SkippedSetupCaseResult,
)
from protostar.testing.test_suite import TestCase


async def run_setup_case(
    test_case: TestCase,
    state: TestExecutionState,
    project_compiler: ProjectCompiler,
) -> SetupCaseResult:
    assert test_case.setup_fn_name

    try:
        execution_environment = SetupCaseExecutionEnvironment(state, project_compiler)

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
