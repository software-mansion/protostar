from pathlib import Path

import pytest

from tests.integration.conftest import (
    ProtostarFixture,
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH

CURRENT_DIR = Path(__file__).parent


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_l1_to_l2_message_cheatcode(
    protostar: ProtostarFixture,
):
    protostar.create_contracts(
        {
            "l1_handler_contract": CONTRACTS_PATH / "l1_handler_contract.cairo",
            "roll_warp_tester": CONTRACTS_PATH / "roll_warp_tester.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        CURRENT_DIR / "send_message_to_l2_cairo_cheatcode_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_happy_path",
            "test_other_cheatcodes_impact_l1_handler",
            "test_other_cheatcodes_impact_contracts_called_from_l1_handler",
        ],
    )
