from pathlib import Path

from tests.integration.conftest import (
    RunTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_roll_cheatcode(run_test_runner: RunTestRunnerFixture):
    testing_summary = await run_test_runner(
        Path(__file__).parent / "roll_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_changing_block_number",
            "test_changing_block_number_in_deployed_contract",
        ],
        expected_failed_test_cases_names=[],
    )
