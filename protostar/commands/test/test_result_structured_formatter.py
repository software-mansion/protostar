from typing import Any, Literal, Optional
from dataclasses import dataclass
from pathlib import Path

from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG
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
from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import OutputName

JsonData = dict[str, Any]


@dataclass
# pylint: disable=too-many-instance-attributes
class TestCaseResult(StructuredMessage):
    status: Literal["passed", "failed", "broken", "skipped", "unexpected_exception"]
    test_suite_path: Path

    test_case_name: Optional[str] = None
    execution_time_in_seconds: Optional[float] = None
    exception: Optional[str] = None
    stdout: Optional[dict[OutputName, str]] = None
    traceback: Optional[str] = None
    protostar_message: Optional[str] = None

    fuzz_runs: Optional[int] = None
    gas: Optional[str] = None
    steps: Optional[str] = None
    memory_holes: Optional[str] = None
    builtins: Optional[list[JsonData]] = None

    reason: Optional[str] = None

    type: str = "test_case_result"

    def format_human(self, fmt: LogColorProvider) -> str:
        assert False, "Tests should use live logging for the human-readable output"

    def format_dict(self) -> dict:
        result = {
            "type": self.type,
            "status": self.status,
            "test_suite_path": str(self.test_suite_path),
        }
        if self.test_case_name:
            result["test_case_name"] = self.test_case_name
        if self.execution_time_in_seconds:
            result["execution_time_in_seconds"] = get_formatted_execution_time(
                self.execution_time_in_seconds
            )
        if self.exception:
            result["exception"] = self.exception
        if self.stdout:
            result["stdout"] = str(self.stdout)
        if self.traceback:
            result["traceback"] = self.traceback
        if self.fuzz_runs:
            result["fuzz_runs"] = str(self.fuzz_runs)
        if self.gas:
            result["gas"] = self.gas
        if self.steps:
            result["steps"] = self.steps
        if self.memory_holes:
            result["memory_holes"] = self.memory_holes
        if self.builtins:
            result["builtins"] = str(self.builtins)
        return result


# pylint: disable=too-many-return-statements
def format_test_result_structured(test_result: TestResult) -> TestCaseResult:
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
) -> TestCaseResult:
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
) -> TestCaseResult:
    return TestCaseResult(
        status="failed",
        test_suite_path=failed_test_case_result.file_path,
        test_case_name=failed_test_case_result.test_case_name,
        execution_time_in_seconds=failed_test_case_result.execution_time,
        exception=str(failed_test_case_result.exception),
        stdout=failed_test_case_result.captured_stdout,
    )


def _format_broken_test_case_result(
    broken_test_case_result: BrokenTestCaseResult,
) -> TestCaseResult:
    return TestCaseResult(
        status="broken",
        test_suite_path=broken_test_case_result.file_path,
        test_case_name=broken_test_case_result.test_case_name,
        execution_time_in_seconds=broken_test_case_result.execution_time,
        exception=str(broken_test_case_result.exception),
        stdout=broken_test_case_result.captured_stdout,
    )


def _format_passed_fuzz_test_case_result(
    passed_fuzz_test_case_result: PassedFuzzTestCaseResult,
) -> TestCaseResult:
    result = TestCaseResult(
        status="passed",
        test_suite_path=passed_fuzz_test_case_result.file_path,
        test_case_name=passed_fuzz_test_case_result.test_case_name,
        execution_time_in_seconds=passed_fuzz_test_case_result.execution_time,
        stdout=passed_fuzz_test_case_result.captured_stdout,
        fuzz_runs=passed_fuzz_test_case_result.fuzz_runs_count,
    )

    if passed_fuzz_test_case_result.execution_resources:
        if passed_fuzz_test_case_result.execution_resources.estimated_gas is not None:
            result.gas = str(
                passed_fuzz_test_case_result.execution_resources.estimated_gas
            )
        if passed_fuzz_test_case_result.execution_resources.n_steps:
            result.steps = str(passed_fuzz_test_case_result.execution_resources.n_steps)
        if passed_fuzz_test_case_result.execution_resources.n_memory_holes:
            result.memory_holes = str(
                passed_fuzz_test_case_result.execution_resources.n_memory_holes
            )

    if passed_fuzz_test_case_result.execution_resources:
        result.builtins = [
            {"name": name, "count": str(count)}
            for name, count in passed_fuzz_test_case_result.execution_resources.builtin_name_to_count_map.items()
        ]

    return result


def _format_skipped_test_case_result(
    skipped_test_case_result: SkippedTestCaseResult,
) -> TestCaseResult:
    return TestCaseResult(
        status="skipped",
        test_suite_path=skipped_test_case_result.file_path,
        test_case_name=skipped_test_case_result.test_case_name,
        reason=skipped_test_case_result.reason,
    )


def _format_failed_fuzz_test_case_result(
    failed_fuzz_test_case_result: FailedFuzzTestCaseResult,
) -> TestCaseResult:
    return _format_failed_test_case_result(failed_fuzz_test_case_result)


def _format_broken_fuzz_test_case_result(
    broken_fuzz_test_case_result: BrokenFuzzTestCaseResult,
) -> TestCaseResult:
    return _format_broken_test_case_result(broken_fuzz_test_case_result)


def _format_broken_test_suite_result(
    broken_test_suite_result: BrokenTestSuiteResult,
) -> TestCaseResult:
    return TestCaseResult(
        status="broken",
        test_suite_path=broken_test_suite_result.file_path,
        exception=str(broken_test_suite_result.exception),
    )


def _format_unexpected_exception_test_suite_result(
    unexpected_exception_test_suite_result: UnexpectedBrokenTestSuiteResult,
) -> TestCaseResult:
    return TestCaseResult(
        status="unexpected_exception",
        test_suite_path=unexpected_exception_test_suite_result.file_path,
        traceback=unexpected_exception_test_suite_result.traceback,
        exception=str(unexpected_exception_test_suite_result.exception),
        protostar_message=UNEXPECTED_PROTOSTAR_ERROR_MSG,
    )


def get_formatted_execution_time(execution_time: float) -> str:
    return f"{execution_time:.2f}"
