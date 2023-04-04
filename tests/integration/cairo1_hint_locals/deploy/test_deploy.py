from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_deploy_hint_local(protostar: ProtostarFixture, shared_datadir: Path):
    protostar.create_contracts(
        {
            "minimal": shared_datadir / "minimal.cairo",
            "with_ctor": shared_datadir / "with_ctor.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "deploy_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploy",
            "test_deploy_with_ctor",
        ],
    )
