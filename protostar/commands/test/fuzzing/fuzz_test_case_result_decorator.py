from typing import Optional

from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_results import (
    FailedFuzzTestCaseResult,
    FailedTestCaseResult,
    FuzzResult,
    FuzzTestExecutionResult,
    PassedFuzzTestCaseResult,
    PassedTestCaseResult,
    TestCaseResultDecorator,
)


class FuzzTestCaseResultDecorator(TestCaseResultDecorator):
    def decorate_passed(
        self,
        result: PassedTestCaseResult,
        execution_result: FuzzTestExecutionResult,
    ) -> PassedTestCaseResult:
        fuzz_result = FuzzResult(fuzz_runs_count=execution_result.fuzz_runs_count)
        return PassedFuzzTestCaseResult.from_passed_test_case_result(
            result, fuzz_result
        )

    def decorate_failed(
        self,
        result: FailedTestCaseResult,
        exception: ReportedException,
    ) -> FailedTestCaseResult:
        fuzz_result = _extract_fuzz_result_from_reported_exception(exception)
        return FailedFuzzTestCaseResult.from_failed_test_case_result(
            result, fuzz_result
        )


def _extract_fuzz_result_from_reported_exception(
    reported_exception: ReportedException,
) -> Optional[FuzzResult]:
    metadata = reported_exception.metadata

    if len(metadata) > 0 and isinstance(metadata[0], FuzzInputExceptionMetadata):
        fuzz_runs_count = reported_exception.execution_info["fuzz_runs"]
        assert isinstance(fuzz_runs_count, int)
        return FuzzResult(fuzz_runs_count)

    return None
