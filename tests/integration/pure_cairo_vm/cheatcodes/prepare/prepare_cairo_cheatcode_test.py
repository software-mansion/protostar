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


async def test_prepare_cheatcode(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "basic_no_constructor": CONTRACTS_PATH / "basic_contract.cairo",
            "basic_with_constructor": CONTRACTS_PATH / "basic_with_constructor.cairo",
            "basic_with_constructor_no_args": CONTRACTS_PATH
            / "basic_with_constructor_no_args.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        TEST_PATH / "prepare_contract_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_preparing_deployment_with_constructor_no_args",
            "test_preparing_deployment_with_constructor_data_transformer",
            "test_preparing_deployment_no_constructor",
            "test_preparing_deployment_with_constructor_no_data_transformer",
        ],
    )
