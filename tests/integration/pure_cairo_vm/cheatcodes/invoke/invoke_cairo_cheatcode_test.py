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


async def test_invoke(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "basic": CONTRACTS_PATH / "basic_contract.cairo",
            "proxy": CONTRACTS_PATH / "proxy_for_basic_contract.cairo",
            "panic": CONTRACTS_PATH / "panicking_contract.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        TEST_PATH / "invoke_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_invoke_without_transformation",
            "test_panicking",
            "test_invoke_with_transformation",
            "test_invoke_with_proxy",
        ],
    )
