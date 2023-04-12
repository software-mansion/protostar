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


async def test_prepare_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "minimal_no_args": shared_datadir / "minimal_no_args.cairo",
            "minimal_with_args": shared_datadir / "minimal_with_args.cairo",
        }
    )

    testing_summary = await protostar_project.protostar.run_test_runner(
        Path(__file__).parent / "prepare_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_prepare_no_args",
            "test_prepare_with_args",
        ],
    )
