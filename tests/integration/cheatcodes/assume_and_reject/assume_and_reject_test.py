from pathlib import Path

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_assume_and_reject_cheatcodes(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "assume_and_reject_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_passed_assume"],
        expected_failed_test_cases_names=[
            "test_assume_not_fuzz",
            "test_reject_not_fuzz",
        ],
    )
