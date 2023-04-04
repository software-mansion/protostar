from pathlib import Path
from textwrap import dedent

import pytest

from protostar.cairo import CairoVersion
from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(cairo_version=CairoVersion.cairo1) as protostar:
        yield protostar


async def test_prepare_hint_local(protostar: ProtostarFixture, shared_datadir: Path):
    protostar.create_contracts(
        {
            "minimal_no_args": shared_datadir / "minimal_no_args.cairo",
            "minimal_with_args": shared_datadir / "minimal_with_args.cairo",
        }
    )
    protostar.create_files(
        {
            "./src/lib.cairo": dedent(
                """
            mod main;
            mod minimal_with_args;
            """
            ),
            "./tests/prepare_test.cairo": Path(__file__).parent / "prepare_test.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        "tests/prepare_test.cairo",
        cairo1_test_runner=True,
        cairo_path=[protostar.project_root_path / "src"],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_prepare_no_args",
            "test_prepare_with_args",
        ],
    )
