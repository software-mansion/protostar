from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    assert_cairo_test_cases,
    CreateProtostarProjectFixture,
)
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_mock_call(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "number_provider": CONTRACTS_PATH / "number_provider_contract.cairo",
            "number_provider_proxy": CONTRACTS_PATH / "number_provider_proxy.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "mock_call_hint_local_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_happy_path", "test_mocking_call_twice"],
    )
