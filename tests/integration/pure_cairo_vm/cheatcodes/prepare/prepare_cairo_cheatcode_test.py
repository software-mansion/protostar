from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration.protostar_fixture import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import RunCairoTestRunnerFixture

CONTRACTS_PATH = Path(__file__).parent.parent / "contracts"
TEST_PATH = Path(__file__).parent


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_prepare_cheatcode(
    protostar: ProtostarFixture, run_cairo_test_runner: RunCairoTestRunnerFixture
):
    protostar.create_files(
        {
            "src/basic_no_constructor.cairo": CONTRACTS_PATH / "basic_contract.cairo",
            "src/basic_with_constructor.cairo": CONTRACTS_PATH
            / "basic_with_constructor.cairo",
            "src/basic_with_constructor_no_args.cairo": CONTRACTS_PATH
            / "basic_with_constructor_no_args.cairo",
        }
    )

    testing_summary = await run_cairo_test_runner(
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
