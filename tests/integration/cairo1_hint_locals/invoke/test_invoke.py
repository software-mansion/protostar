from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_invoke_hint_local(protostar: ProtostarFixture, shared_datadir: Path):
    protostar.create_contracts(
        {
            "get_set": shared_datadir / "get_set.cairo",
            "get_set_with_ctor": shared_datadir / "get_set_with_ctor.cairo",
            "cairo0": shared_datadir / "cairo0.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "invoke_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_invoke_simple",
            "test_invoke_cairo0",
            "test_invoke_with_ctor",
        ],
        expected_failed_test_cases_names=[
            "test_invoke_wrong_number_of_args",
            "test_invoke_non_existing_function",
            "test_invoke_cairo0_wrong_number_of_args",
            "test_invoke_cairo0_non_existing_function",
        ],
    )
