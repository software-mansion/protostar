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


async def test_call_hint_local(protostar: ProtostarFixture, shared_datadir: Path):
    protostar.create_contracts(
        {
            "simple": shared_datadir / "simple.cairo",
            "with_ctor": shared_datadir / "with_ctor.cairo",
            "with_ctor_panic": shared_datadir / "with_ctor_panic.cairo",
            "cairo0": shared_datadir / "cairo0.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "call_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_call_simple",
            "test_call_with_ctor",
            "test_call_cairo0",
        ],
        expected_failed_test_cases_names=[
            "test_call_wrong_name",
            "test_call_wrong_number_of_args",
            "test_call_cairo0_non_existing_entrypoint",
        ],
    )
