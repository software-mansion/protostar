from pathlib import Path

from tests.integration.conftest import (
    RunCairo0TestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_testing_steps(
    run_cairo0_test_runner: RunCairo0TestRunnerFixture,
):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "testing_steps_test.cairo", max_steps=10
    )

    assert_cairo_test_cases(
        testing_summary, expected_failed_test_cases_names=["test_max_steps"]
    )

    assert "OUT_OF_RESOURCES" in str(testing_summary.failed[0].exception)

    ###

    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "testing_steps_test.cairo", max_steps=-1
    )

    assert_cairo_test_cases(
        testing_summary, expected_passed_test_cases_names=["test_max_steps"]
    )

    ###

    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "testing_steps_test.cairo", max_steps=1000
    )

    assert_cairo_test_cases(
        testing_summary, expected_passed_test_cases_names=["test_max_steps"]
    )
