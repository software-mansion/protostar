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
        expected_failed_test_cases_names=["test_skip_outside_of_setup"],
        expected_skipped_test_cases_names=[
            "test_skip",
            "test_skip_no_reason",
        ],
    )

    output = get_formatted_output(testing_summary.skipped)
    assert "REASON" in output


def get_formatted_output(
    skipped_test_case_results: List[SkippedTestCaseResult]
):
    output = ""
    for test_case_result in skipped_test_case_results:
        output += format_test_result(test_case_result)
    return output

