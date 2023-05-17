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


async def test_start_roll_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts_cairo1(
        {
            "simple": shared_datadir / "simple",
            "proxy": shared_datadir / "proxy",
            "storing_block_number": shared_datadir / "storing_block_number",
            "storing_constructor_blk_number": shared_datadir
            / "storing_constructor_blk_number",
        }
    )

    testing_summary = await protostar_project.protostar.test(
        Path(__file__).parent / "start_roll_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_start_roll",
            "test_start_roll_behind_a_proxy",
            "test_start_roll_with_invoke",
            "test_start_roll_constructor",
            "test_start_stop_roll",
            "test_stop_roll_on_non_existent",
            "test_stop_roll_on_not_rolled",
            "test_stop_roll_multiple_times",
            "test_start_roll_last_value_is_used",
        ],
    )
