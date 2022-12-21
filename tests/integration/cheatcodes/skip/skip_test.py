from pathlib import Path

from tests.integration.conftest import (
    RunTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_skip(
    run_test_runner: RunTestRunnerFixture,
):
    testing_summary = await run_test_runner(Path(__file__).parent / "skip_test.cairo")

    assert_cairo_test_cases(
        testing_summary,
        expected_failed_test_cases_names=["test_skip_outside_of_setup"],
        expected_skipped_test_cases_names=[
            "test_skip",
            "test_skip_no_reason",
        ],
    )
