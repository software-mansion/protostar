from pathlib import Path

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_store_cheatcode(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "store_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_store_in_deployed_contract",
            "test_store_map_in_deployed_contract",
            "test_store_map_complex_key_in_deployed_contract",
            "test_store_map_struct_key_in_deployed_contract",
            "test_store_map_struct_val_in_deployed_contract",
            "test_map_store_local",
        ],
        expected_failed_test_cases_names=[],
    )
