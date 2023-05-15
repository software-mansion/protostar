from pathlib import Path

from tests.integration.conftest import (
    RunCairo0TestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_skip(
    run_cairo0_test_runner: RunCairo0TestRunnerFixture,
):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "skip_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_failed_test_cases_names=["test_skip_outside_of_setup"],
        expected_skipped_test_cases_names=[
            "test_skip",
            "test_skip_no_reason",
        ],
    )
