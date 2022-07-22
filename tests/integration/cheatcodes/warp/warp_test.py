from pathlib import Path

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_warp_cheatcode(run_cairo_test_runner: RunCairoTestRunnerFixture):

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "warp_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_changing_timestamp",
            "test_changing_timestamp_in_deployed_contract",
        ],
        expected_failed_test_cases_names=[],
    )
