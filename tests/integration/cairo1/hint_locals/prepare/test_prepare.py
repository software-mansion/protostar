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


async def test_prepare_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts_cairo1(
        {
            "minimal_no_ctor": shared_datadir / "minimal_no_ctor",
            "minimal_no_args": shared_datadir / "minimal_no_args",
            "minimal_with_args": shared_datadir / "minimal_with_args",
        }
    )
    protostar_project.create_contracts(
        {
            "cairo0": shared_datadir / "cairo0.cairo",
            "cairo0_w_ctor": shared_datadir / "cairo0_w_ctor.cairo",
            "cairo0_w_ctor_no_args": shared_datadir / "cairo0_w_ctor_no_args.cairo",
        }
    )

    testing_summary = await protostar_project.protostar.test(
        Path(__file__).parent / "prepare_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_prepare_no_ctor",
            "test_prepare_no_args",
            "test_prepare_with_args",
            "test_prepare_cairo0",
            "test_prepare_cairo0_w_ctor",
            "test_prepare_cairo0_w_ctor_no_args",
            "test_prepare_doesnt_move_calldata",
        ],
    )
