from pathlib import Path

from tests.integration.conftest import (
    RunTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_load_cheatcode(run_test_runner: RunTestRunnerFixture):
    testing_summary = await run_test_runner(
        Path(__file__).parent / "load_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_load_in_user_contract",
            "test_load_map_in_user_contract",
            "test_load_map_complex_key_in_user_contract",
            "test_load_map_struct_key_in_user_contract",
            "test_load_map_struct_val_in_user_contract",
            "test_map_load_local",
        ],
        expected_broken_test_cases_names=["test_missing_type_name"],
    )

    assert "ValueB has not been found in contract" in str(
        testing_summary.broken[0].exception
    )
