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


async def test_declare_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "minimal": shared_datadir / "minimal.cairo",
            "broken": shared_datadir / "broken.cairo",
            "cairo0": shared_datadir / "cairo0.cairo",
        }
    )

    testing_summary = await protostar_project.protostar.run_test_runner(
        Path(__file__).parent / "declare_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_declare",
        ],
        expected_broken_test_cases_names=[
            "test_declare_nonexistent",
            "test_declare_broken",
            "test_declare_cairo0",
        ],
    )
