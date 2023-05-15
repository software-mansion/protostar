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


async def test_call_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts(
        {
            "cairo0": shared_datadir / "cairo0.cairo",
        }
    )
    protostar_project.create_contracts_cairo1(
        {
            "simple": shared_datadir / "simple",
            "with_ctor": shared_datadir / "with_ctor",
            "with_storage": shared_datadir / "with_storage",
            "with_ctor_panic": shared_datadir / "with_ctor_panic",
            "panicking_contract": shared_datadir / "panicking_contract",
        }
    )

    testing_summary = await protostar_project.protostar.test(
        Path(__file__).parent / "call_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_call_simple",
            "test_call_not_mutating_state",
            "test_call_cairo0",
            "test_call_exception_handling",
            "test_call_doesnt_move_calldata",
        ],
        expected_failed_test_cases_names=[
            "test_call_wrong_name",
            "test_call_wrong_number_of_args",
            "test_call_cairo0_non_existing_entrypoint",
        ],
    )
