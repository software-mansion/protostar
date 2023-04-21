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


async def test_prank_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts_cairo1({"pranked": shared_datadir / "pranked"})

    testing_summary = await protostar_project.protostar.run_test_runner(
        Path(__file__).parent / "prank_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_prank",
            "test_stop_prank_on_non_existent",
            "test_stop_prank_on_not_pranked",
            "test_stop_prank_multiple_times",
            "test_start_prank_latest_takes_precedence",
            "test_stop_prank_cancels_all_pranks",
        ],
    )
