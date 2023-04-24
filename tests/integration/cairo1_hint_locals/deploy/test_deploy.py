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


async def test_deploy_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "cairo0": shared_datadir / "cairo0.cairo",
        }
    )
    protostar_project.create_contracts_cairo1(
        {
            "minimal": shared_datadir / "minimal",
            "with_storage": shared_datadir / "with_storage",
            "with_ctor": shared_datadir / "with_ctor",
            "with_ctor_panic": shared_datadir / "with_ctor_panic",
        }
    )

    testing_summary = await protostar_project.protostar.test_cairo1(
        Path(__file__).parent / "deploy_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy",
            "test_deploy_cairo0",
            "test_deploy_with_ctor",
            "test_deploy_with_storage",
            "test_deploy_with_ctor_panic_check_err_code",
        ],
        expected_failed_test_cases_names=[
            "test_deploy_with_ctor_invalid_calldata",
            "test_deploy_with_ctor_panic",
        ],
    )
