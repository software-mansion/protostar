from typing import Callable
import json
import math

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
from protostar.starknet.data_transformer import PythonData

LogCallback = Callable[[str], None]


# pylint: disable=too-many-return-statements
def format_test_result_structured(test_result: TestResult) -> str:
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
) -> str:
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
) -> str:
    result: PythonData = {
        "type": "test_case_result",
        "status": "failed",
        "test_suite_path": str(failed_test_case_result.file_path),
        "test_case_name": failed_test_case_result.test_case_name,
        "execution_time_in_seconds": get_formatted_execution_time(
            failed_test_case_result.execution_time
        ),
        "exception": {"message": str(failed_test_case_result.exception)},
        "stdout": failed_test_case_result.captured_stdout,
    }

    return json.dumps(result)


def _format_broken_test_case_result(
    broken_test_case_result: BrokenTestCaseResult,
) -> str:
    result: PythonData = {
        "type": "test_case_result",
        "status": "broken",
        "test_suite_path": str(broken_test_case_result.file_path),
        "test_case_name": broken_test_case_result.test_case_name,
        "execution_time_in_seconds": get_formatted_execution_time(
            broken_test_case_result.execution_time
        ),
        "exception": {"message": broken_test_case_result.exception},
        "stdout": broken_test_case_result.captured_stdout,
    }

    return json.dumps(result)


def _format_passed_fuzz_test_case_result(
    passed_fuzz_test_case_result: PassedFuzzTestCaseResult,
) -> str:
    result: PythonData = {
        "type": "test_case_result",
        "status": "passed",
        "test_suite_path": str(passed_fuzz_test_case_result.file_path),
        "test_case_name": passed_fuzz_test_case_result.test_case_name,
        "execution_time_in_seconds": get_formatted_execution_time(
            passed_fuzz_test_case_result.execution_time
        ),
        "stdout": passed_fuzz_test_case_result.captured_stdout,
    }

    if passed_fuzz_test_case_result.fuzz_runs_count is not None:
        result["fuzz_runs"] = passed_fuzz_test_case_result.fuzz_runs_count

    if passed_fuzz_test_case_result.execution_resources:
        if passed_fuzz_test_case_result.execution_resources.estimated_gas is not None:
            result[
                "gas"
            ] = passed_fuzz_test_case_result.execution_resources.estimated_gas
        if passed_fuzz_test_case_result.execution_resources.n_steps:
            result["steps"] = str(
                passed_fuzz_test_case_result.execution_resources.n_steps
            )
        if passed_fuzz_test_case_result.execution_resources.n_memory_holes:
            result[
                "memory_holes"
            ] = passed_fuzz_test_case_result.execution_resources.n_memory_holes

    if passed_fuzz_test_case_result.execution_resources:
        result["builtins"] = [
            {"name": name, "count": count}
            for name, count in passed_fuzz_test_case_result.execution_resources.builtin_name_to_count_map.items()
        ]

    return json.dumps(result)


def _format_skipped_test_case_result(skipped_test_case_result: SkippedTestCaseResult):
    result: PythonData = {
        "type": "test_case_result",
        "status": "skipped",
        "test_suite_path": str(skipped_test_case_result.file_path),
        "test_case_name": skipped_test_case_result.test_case_name,
    }

    reason = skipped_test_case_result.reason
    if reason is not None:
        result["reason"] = reason

    return json.dumps(result)


def _format_failed_fuzz_test_case_result(
    failed_fuzz_test_case_result: FailedFuzzTestCaseResult,
) -> str:
    return _format_failed_test_case_result(failed_fuzz_test_case_result)


def _format_broken_fuzz_test_case_result(
    broken_fuzz_test_case_result: BrokenFuzzTestCaseResult,
) -> str:
    return _format_broken_test_case_result(broken_fuzz_test_case_result)


def _format_broken_test_suite_result(
    broken_test_suite_result: BrokenTestSuiteResult,
) -> str:
    result: PythonData = {
        "type": "test_case_result",
        "status": "broken",
        "test_suite_path": str(broken_test_suite_result.file_path),
        "exception": broken_test_suite_result.exception,
    }

    return json.dumps(result)


def _format_unexpected_exception_test_suite_result(
    unexpected_exception_test_suite_result: UnexpectedBrokenTestSuiteResult,
) -> str:
    result: PythonData = {
        "type": "test_case_result",
        "status": "unexpected_exception",
        "test_suite_path": str(unexpected_exception_test_suite_result.file_path),
        "traceback": unexpected_exception_test_suite_result.traceback,
        "exception": str(unexpected_exception_test_suite_result.exception),
        "protostar_message": UNEXPECTED_PROTOSTAR_ERROR_MSG,
    }

    return json.dumps(result)


def get_formatted_execution_time(execution_time: float) -> float:
    return math.floor(execution_time * 100) / 100
