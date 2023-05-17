from pathlib import Path

from tests.integration.conftest import (
    RunCairo0TestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_testing_hooks(run_cairo0_test_runner: RunCairo0TestRunnerFixture):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "testing_hooks_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_contract_was_deployed_in_setup",
        ],
        expected_failed_test_cases_names=[],
    )


async def test_setup_case(run_cairo0_test_runner: RunCairo0TestRunnerFixture):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "setup_case_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_setup_case",
            "test_setup_hook_only",
        ],
        expected_broken_test_cases_names=[
            "test_setup_case_fails",
        ],
    )


async def test_invalid_setup(run_cairo0_test_runner: RunCairo0TestRunnerFixture):
    testing_summary = await run_cairo0_test_runner(
        Path(__file__).parent / "invalid_setup_test.cairo"
    )

    assert len(testing_summary.broken_suites) == 1
