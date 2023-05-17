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
        return PassedFuzzTestCaseResultMessage(test_result)
    if isinstance(test_result, FailedFuzzTestCaseResult):
        return FailedTestCaseResultMessage(test_result)
    if isinstance(test_result, BrokenFuzzTestCaseResult):
        return BrokenTestCaseResultMessage(test_result)
    if isinstance(test_result, PassedTestCaseResult):
        return PassedFuzzTestCaseResultMessage(
            PassedFuzzTestCaseResult(
                captured_stdout=test_result.captured_stdout,
                execution_resources=test_result.execution_resources,
                file_path=test_result.file_path,
                execution_time=test_result.execution_time,
                test_case_name=test_result.test_case_name,
                fuzz_runs_count=None,
            )
        )
    if isinstance(test_result, FailedTestCaseResult):
        return FailedTestCaseResultMessage(test_result)
    if isinstance(test_result, BrokenTestCaseResult):
        return BrokenTestCaseResultMessage(test_result)
    if isinstance(test_result, SkippedTestCaseResult):
        return SkippedTestCaseResultMessage(test_result)
    if isinstance(test_result, UnexpectedBrokenTestSuiteResult):
        return UnexpectedBrokenTestSuiteResultMessage(test_result)
    if isinstance(test_result, BrokenTestSuiteResult):
        return BrokenTestSuiteResultMessage(test_result)
    raise NotImplementedError("Unreachable")
