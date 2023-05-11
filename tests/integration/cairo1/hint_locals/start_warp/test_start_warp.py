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


async def test_start_warp_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts_cairo1(
        {
            "simple": shared_datadir / "simple",
            "proxy": shared_datadir / "proxy",
            "storing_timestamp": shared_datadir / "storing_timestamp",
            "storing_constructor_timestamp": shared_datadir
            / "storing_constructor_timestamp",
        }
    )

    testing_summary = await protostar_project.protostar.test_cairo1(
        Path(__file__).parent / "start_warp_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_start_warp",
            "test_start_warp_behind_a_proxy",
            "test_start_warp_with_invoke",
            "test_start_warp_constructor",
            "test_start_stop_warp",
            "test_stop_warp_on_non_existent",
            "test_stop_warp_on_not_warped",
            "test_stop_warp_multiple_times",
            "test_start_warp_last_value_is_used",
        ],
    )
