from pathlib import Path

from tests.integration.conftest import (
    RunCairo0TestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_prepare_cheatcode(run_cairo0_test_runner: RunCairo0TestRunnerFixture):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "prepare_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_passing_constructor_data_as_list",
            "test_data_transformation",
            "test_address_can_be_created_deterministically",
        ],
        expected_failed_test_cases_names=[],
    )
