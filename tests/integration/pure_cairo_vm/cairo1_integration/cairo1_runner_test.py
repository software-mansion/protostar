from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_cairo_1_runner(protostar: ProtostarFixture, shared_datadir: Path):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )
    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "test_cairo1.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_cairo1::test_cairo1::passing_test",
        ],
    )
