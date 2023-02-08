from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH

TEST_PATH = Path(__file__).parent / "declare_contract_test.cairo"


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_declare(protostar: ProtostarFixture):
    protostar.create_contracts({"basic": CONTRACTS_PATH / "basic_contract.cairo"})

    testing_summary = await protostar.run_test_runner(TEST_PATH, cairo_test_runner=True)

    assert_cairo_test_cases(
        testing_summary, expected_passed_test_cases_names=["test_declaring_contract"]
    )


async def test_using_compiled_contracts(protostar: ProtostarFixture):
    protostar.create_contracts({"basic": CONTRACTS_PATH / "basic_contract.cairo"})
    build_output_path = protostar.project_root_path / "build"

    testing_summary = await protostar.run_test_runner(
        TEST_PATH,
        cairo_test_runner=True,
        compiled_contracts_path=build_output_path,
    )
    assert not testing_summary.passed

    await protostar.build()
    testing_summary = await protostar.run_test_runner(
        TEST_PATH,
        cairo_test_runner=True,
        compiled_contracts_path=build_output_path,
    )

    assert_cairo_test_cases(
        testing_summary, expected_passed_test_cases_names=["test_declaring_contract"]
    )
