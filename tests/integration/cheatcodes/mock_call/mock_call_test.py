from pathlib import Path

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.mark.asyncio
async def test_mock_call(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "mock_call_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_remote_mock",
            "test_local_mock",
            "test_missing_remote_mock",
            "test_missing_local_mock",
            "test_syscall_counter_updated",
            "test_mock_call_wrong_target",
            "test_mock_call_wrong_selector_target",
            "test_data_transformation",
            "test_data_transformation_in_contract_from_setup",
            "test_data_transformation_with_syscall_deploy",
            "test_library_call_not_affected_by_mock",
        ],
        expected_broken_test_cases_names=["test_mock_call_twice"],
    )
