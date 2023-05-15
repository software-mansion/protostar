from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar_project", scope="function")
def protostar_project_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_deploy_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "cairo0": shared_datadir / "cairo0.cairo",
            "cairo0_w_ctor": shared_datadir / "cairo0_w_ctor.cairo",
            "cairo0_w_ctor_error": shared_datadir / "cairo0_w_ctor_error.cairo",
        }
    )

    testing_summary = await protostar_project.protostar.test_cairo1(
        Path(__file__).parent / "deploy_contract_cairo0_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy_contract_cairo0",
            "test_deploy_contract_cairo0_w_ctor",
            "test_deploy_contract_cairo0_doesnt_move_calldata",
        ],
        expected_failed_test_cases_names=[
            "test_deploy_contract_cairo0_w_ctor_error",
        ],
    )
