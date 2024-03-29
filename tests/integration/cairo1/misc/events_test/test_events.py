from pathlib import Path

import pytest

from protostar.cairo import CairoVersion
from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar_project", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(CairoVersion.cairo1) as protostar_project:
        yield protostar_project


async def test_deploy_contract_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts_cairo1(
        {
            "simple": shared_datadir / "simple",
            "with_data": shared_datadir / "with_data",
        }
    )

    testing_summary = await protostar_project.protostar.test(
        Path(__file__).parent / "events_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_events_simple",
            "test_events_with_data",
        ],
    )
