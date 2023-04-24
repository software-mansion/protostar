from pathlib import Path

import pytest

from protostar.cairo import CairoVersion
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarProjectFixture


@pytest.fixture(autouse=True, name="protostar_project")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(
        cairo_version=CairoVersion.cairo1
    ) as protostar_project:
        yield protostar_project


async def test_declare_cairo0_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "basic_contract_cairo0": shared_datadir / "basic_contract.cairo",
            "broken_syntax_contract": shared_datadir / "broken_syntax_contract.cairo",
        },
    )
    testing_summary = await protostar_project.protostar.run_test_runner(
        Path(__file__).parent / "declare_cairo0_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_declaring_contract"],
        expected_failed_test_cases_names=[
            "test_failing_to_declare_contract",
            "test_declaring_broken_contract",
        ],
    )
