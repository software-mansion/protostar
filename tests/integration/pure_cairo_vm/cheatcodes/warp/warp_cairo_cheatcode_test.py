from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import (
    CONTRACTS_PATH,
)

TEST_PATH = Path(__file__).parent


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_warp_cheatcode(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "main": CONTRACTS_PATH / "warp_contract.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(TEST_PATH / "warp_test.cairo")

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_warp",
            "test_warp_with_invoke",
            "test_warp_with_invoke_depth_2",
        ],
    )
