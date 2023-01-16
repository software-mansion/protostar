from pathlib import Path

from tests.integration.conftest import assert_cairo_test_cases
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture


async def test_prank_cheatcode(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "prank_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_not_fails_when_pranked",
            "test_not_fails_when_pranked_wrong_target",
        ],
        expected_failed_test_cases_names=[
            "test_fails_when_not_pranked",
            "test_fails_when_different_target_is_pranked",
        ],
    )
