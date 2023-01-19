import asyncio
from pathlib import Path

from tests.integration.conftest import assert_cairo_test_cases
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture

CURRENT_DIR = Path(__file__).parent


def test_l1_to_l2_message_cheatcode(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):

    testing_summary = asyncio.run(
        run_cairo_test_runner(
            Path(CURRENT_DIR / "send_message_to_l2_cairo_cheatcode_test.cairo")
        )
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_happy_path",
            "test_data_transformer",
            "test_other_cheatcodes_impact_l1_handler",
        ],
    )
