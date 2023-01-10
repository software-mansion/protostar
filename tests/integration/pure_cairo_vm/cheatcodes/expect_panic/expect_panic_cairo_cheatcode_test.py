import asyncio
from pathlib import Path

import pytest

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.testing import TestingSummary
from protostar.testing.test_results import BrokenTestCaseResult
from tests.integration.conftest import assert_cairo_test_cases
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture


@pytest.fixture(name="testing_summary", scope="module")
def testing_summary_fixture(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
) -> TestingSummary:

    return asyncio.run(
        run_cairo_test_runner(
            Path(__file__).parent / "expect_panic_test.cairo",
        )
    )


async def test_test_result_types(testing_summary: TestingSummary):
    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_inner_error_message",
            "test_outer_error_message",
            "test_partial_error_message",
            "test_no_error_message_when_error_is_annotated",
            "test_no_error_message_when_error_is_not_annotated",
        ],
        expected_failed_test_cases_names=[
            "test_fail_when_expected_panic",
            "test_fail_error_message",
            "test_fail",
        ],
        expected_broken_test_cases_names=["test_broken_when_panic_is_already_expected"],
    )


async def test_broken_when_panic_is_already_expected(
    testing_summary: TestingSummary,
):

    test_result = testing_summary["test_broken_when_panic_is_already_expected"]
    formatted_test_result = format_test_result(test_result)

    assert isinstance(test_result, BrokenTestCaseResult)
    assert "matching the following error" not in formatted_test_result
    assert "Protostar is already expecting an exception" in formatted_test_result
