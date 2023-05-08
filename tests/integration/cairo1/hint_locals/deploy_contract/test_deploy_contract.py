from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar_project", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        yield protostar_project


async def test_deploy_contract_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "cairo0": shared_datadir / "cairo0.cairo",
            "cairo0_with_constructor": shared_datadir / "cairo0_with_constructor.cairo",
        }
    )
    protostar_project.create_contracts_cairo1(
        {
            "minimal": shared_datadir / "minimal",
            "with_constructor": shared_datadir / "with_constructor",
            "with_constructor_panic": shared_datadir / "with_constructor_panic",
        }
    )

    testing_summary = await protostar_project.protostar.test_cairo1(
        Path(__file__).parent / "deploy_contract_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_contract_minimal",
            "test_deploy_contract_with_constructor",
            "test_deploy_contract_cairo0",
            "test_deploy_contract_cairo0_with_constructor",
        ],
        expected_failed_test_cases_names=[
            "test_deploy_contract_with_constructor_panic",
        ],
        expected_broken_test_cases_names=[
            "test_deploy_non_existing_contract",
            "test_deploy_contract_cairo0_using_cairo1",
        ],
    )
