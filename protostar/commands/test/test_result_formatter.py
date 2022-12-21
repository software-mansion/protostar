from typing import Callable

from protostar.testing import (
    BrokenFuzzTestCaseResult,
    BrokenTestCaseResult,
    BrokenTestSuiteResult,
    FailedFuzzTestCaseResult,
    FailedTestCaseResult,
    PassedFuzzTestCaseResult,
    PassedTestCaseResult,
    SkippedTestCaseResult,
    TestResult,
    UnexpectedBrokenTestSuiteResult,
)
from protostar.io import StructuredMessage

from .messages import (
    BrokenTestSuiteResultMessage,
    BrokenTestCaseResultMessage,
    FailedTestCaseResultMessage,
    PassedFuzzTestCaseResultMessage,
    SkippedTestCaseResultMessage,
    UnexpectedBrokenTestSuiteResultMessage,
)

LogCallback = Callable[[str], None]


# pylint: disable=too-many-return-statements
def format_test_result(test_result: TestResult) -> StructuredMessage:
    if isinstance(test_result, PassedFuzzTestCaseResult):
        return _format_passed_fuzz_test_case_result(test_result)
    if isinstance(test_result, FailedFuzzTestCaseResult):
        return _format_failed_fuzz_test_case_result(test_result)
    if isinstance(test_result, BrokenFuzzTestCaseResult):
        return _format_broken_fuzz_test_case_result(test_result)
    if isinstance(test_result, PassedTestCaseResult):
        return _format_passed_test_case_result(test_result)
    if isinstance(test_result, FailedTestCaseResult):
        return _format_failed_test_case_result(test_result)
    if isinstance(test_result, BrokenTestCaseResult):
        return _format_broken_test_case_result(test_result)
    if isinstance(test_result, SkippedTestCaseResult):
        return _format_skipped_test_case_result(test_result)
    if isinstance(test_result, UnexpectedBrokenTestSuiteResult):
        return _format_unexpected_exception_test_suite_result(test_result)
    if isinstance(test_result, BrokenTestSuiteResult):
        return _format_broken_test_suite_result(test_result)
    raise NotImplementedError("Unreachable")


def _format_passed_test_case_result(
    passed_test_case_result: PassedTestCaseResult,
) -> PassedFuzzTestCaseResultMessage:
    return _format_passed_fuzz_test_case_result(
        PassedFuzzTestCaseResult(
            captured_stdout=passed_test_case_result.captured_stdout,
            execution_resources=passed_test_case_result.execution_resources,
            file_path=passed_test_case_result.file_path,
            execution_time=passed_test_case_result.execution_time,
            test_case_name=passed_test_case_result.test_case_name,
            fuzz_runs_count=None,
        )
    )


def _format_failed_test_case_result(
    failed_test_case_result: FailedTestCaseResult,
) -> FailedTestCaseResultMessage:
    return FailedTestCaseResultMessage(failed_test_case_result=failed_test_case_result)


def _format_broken_test_case_result(
    broken_test_case_result: BrokenTestCaseResult,
) -> BrokenTestCaseResultMessage:
    return BrokenTestCaseResultMessage(broken_test_case_result=broken_test_case_result)


def _format_passed_fuzz_test_case_result(
    passed_fuzz_test_case_result: PassedFuzzTestCaseResult,
) -> PassedFuzzTestCaseResultMessage:
    return PassedFuzzTestCaseResultMessage(
        passed_fuzz_test_case_result=passed_fuzz_test_case_result
    )


def _format_skipped_test_case_result(skipped_test_case_result: SkippedTestCaseResult):
    return SkippedTestCaseResultMessage(
        skipped_test_case_result=skipped_test_case_result
    )


def _format_failed_fuzz_test_case_result(
    failed_fuzz_test_case_result: FailedFuzzTestCaseResult,
) -> FailedTestCaseResultMessage:
    return _format_failed_test_case_result(failed_fuzz_test_case_result)


def _format_broken_fuzz_test_case_result(
    broken_fuzz_test_case_result: BrokenFuzzTestCaseResult,
) -> BrokenTestCaseResultMessage:
    return _format_broken_test_case_result(broken_fuzz_test_case_result)


def _format_broken_test_suite_result(
    broken_test_suite_result: BrokenTestSuiteResult,
) -> BrokenTestSuiteResultMessage:
    return BrokenTestSuiteResultMessage(
        broken_test_suite_result=broken_test_suite_result
    )


def _format_unexpected_exception_test_suite_result(
    unexpected_exception_test_suite_result: UnexpectedBrokenTestSuiteResult,
) -> UnexpectedBrokenTestSuiteResultMessage:
    return UnexpectedBrokenTestSuiteResultMessage(
        unexpected_exception_test_suite_result=unexpected_exception_test_suite_result
    )
