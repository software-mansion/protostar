from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    assert_cairo_test_cases,
    CreateProtostarProjectFixture,
)
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_load_cheatcode(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "block_number_contract": CONTRACTS_PATH / "block_number_contract.cairo",
            "deployer": CONTRACTS_PATH / "deployer.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "load_test.cairo",
        cairo_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_load",
            "test_load_map",
            "test_load_map_complex_key",
            "test_load_map_struct_key",
            "test_load_map_struct_val",
            "test_loading_from_contract_deployed_by_syscall",
        ],
        expected_broken_test_cases_names=["test_missing_type_name"],
    )

    assert "ValueB has not been found in contract" in str(
        testing_summary.broken[0].exception
    )
