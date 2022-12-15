from pathlib import Path

from tests.integration.conftest import (
    RunTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_prank_cheatcode(run_test_runner: RunTestRunnerFixture):
    testing_summary = await run_test_runner(
        Path(__file__).parent / "prank_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_remote_prank",
            "test_local_prank",
            "test_pranks_only_target",
            "test_syscall_counter_correct",
            "test_missing_remote_prank",
            "test_missing_local_prank",
            "test_prank_wrong_target",
        ],
        expected_broken_test_cases_names=[
            "test_fails_but_cannot_freeze_when_cheatcode_exception_is_raised"
        ],
    )
