from pathlib import Path
from typing import List

import pytest

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.commands.test.test_results import SkippedTestCaseResult

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.mark.asyncio
async def test_testing_output(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "skipping_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_skip_false",
        ],
        expected_failed_test_cases_names=["test_skip_false_failed"],
        expected_skipped_test_cases_names=[
            "test_skip",
            "test_skip_failed",
            "test_skip_no_reason",
            "test_skip_no_input",
        ],
    )

    assert_any_has_key_as_reason(testing_summary.skipped, "AAA")
    assert_any_has_key_as_reason(testing_summary.skipped, "CCC")
    assert_none_have_key_as_reason(testing_summary.skipped, "BBB")
    assert_none_have_key_as_reason(testing_summary.skipped, "DDD")


def assert_any_has_key_as_reason(
    skipped_test_case_results: List[SkippedTestCaseResult], key
):
    for test_case_result in skipped_test_case_results:
        output = format_test_result(test_case_result)
        if key in output:
            return True
    return False


def assert_none_have_key_as_reason(
    skipped_test_case_results: List[SkippedTestCaseResult], key
):
    for test_case_result in skipped_test_case_results:
        output = format_test_result(test_case_result)
        if key in output:
            return False
    return True
