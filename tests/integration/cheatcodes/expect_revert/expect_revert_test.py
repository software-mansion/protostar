import asyncio
from pathlib import Path

import pytest

from protostar.testing import TestingSummary
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
    get_protostar_test_case_result,
)


@pytest.fixture(name="testing_summary", scope="module")
def testing_summary_fixture(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
) -> TestingSummary:
    return asyncio.run(
        run_cairo_test_runner(Path(__file__).parent / "expect_revert_test.cairo")
    )


async def test_test_result_types(testing_summary: TestingSummary):
    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_partial_error_message",
            "test_call_not_existing_contract_err_message",
            "test_call_not_existing_contract",
            "test_error_message",
            "test_with_except_revert",
        ],
        expected_failed_test_cases_names=[
            "test_error_was_not_raised_before_stopping_expect_revert_fail_expected",
            "test_call_not_existing_contract_fail_expected",
            "test_with_except_out_of_scope_revert_fail_expected",
            "test_with_except_revert_fail_expected",
            "test_fail_error_message",
        ],
        expected_broken_test_cases_names=[
            "test_already_expecting_error_message_when_no_arguments_were_provided"
        ],
    )


async def test_already_expecting_error_message_when_no_arguments_were_provided(
    testing_summary: TestingSummary,
):
    (_, formatted_protostar_test_result) = get_protostar_test_case_result(
        testing_summary,
        "test_already_expecting_error_message_when_no_arguments_were_provided",
    )

    assert "matching the following error" not in formatted_protostar_test_result
    assert (
        "Protostar is already expecting an exception" in formatted_protostar_test_result
    )
