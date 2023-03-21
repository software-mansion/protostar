from pathlib import Path

import pytest

from protostar.cairo import CairoVersion
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(cairo_version=CairoVersion.cairo1) as protostar:
        yield protostar


async def test_declare_cairo0(protostar: ProtostarFixture, datadir: Path):
    protostar.create_contracts(
        {"basic_contract_cairo0": datadir / "basic_contract.cairo"}
    )
    testing_summary = await protostar.run_test_runner(
        datadir / "declare_cairo0_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_declaring_contract"],
        expected_failed_test_cases_names=["test_failing_to_declaring_contract"],
    )
