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


async def test_stop_roll_cheatcode(protostar: ProtostarFixture):
    protostar.create_files(
        {
            "src/main.cairo": CONTRACTS_PATH / "roll_contract.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        TEST_PATH / "stop_roll_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_stop_roll",
            "test_stop_roll_with_invoke",
        ],
    )
