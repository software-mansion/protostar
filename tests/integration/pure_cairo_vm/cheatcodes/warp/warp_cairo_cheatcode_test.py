from pathlib import Path

from tests.integration.conftest import assert_cairo_test_cases
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture

CONTRACTS_PATH = Path(__file__).parent.parent / "contracts"
TEST_PATH = Path(__file__).parent


async def test_warp_cheatcode(run_cairo_test_runner: RunCairoTestRunnerFixture):

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "warp_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_warp_works",
        ],
    )
