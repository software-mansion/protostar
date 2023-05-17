from pathlib import Path

from tests.integration.conftest import (
    RunCairo0TestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_expect_call(run_cairo0_test_runner: RunCairo0TestRunnerFixture):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "expect_call_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_expect_call_success",
            "test_expect_call_with_stop",
        ],
        expected_failed_test_cases_names=[
            "test_expect_call_after_the_call",
            "test_expect_call_wrong_address",
            "test_expect_call_wrong_calldata",
            "test_expect_call_partial_fail",
            "test_expect_call_expected_but_not_found",
            "test_expect_call_wrong_function_called",
            "test_expect_call_wrong_function_name",
            "test_expect_call_after_stop",
        ],
    )
