from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


CAIRO_PROJECT_CONTENTS = """
    [crate_roots]
    root = "."
"""


async def test_cairo_1_runner(protostar):
    protostar.create_files(
        {
            "cairo_project.toml": CAIRO_PROJECT_CONTENTS,
        }
    )
    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "cairo1_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "passing_test",
        ],
        expected_failed_test_cases_names=[],
    )
