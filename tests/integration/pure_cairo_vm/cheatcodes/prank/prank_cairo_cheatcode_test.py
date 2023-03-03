from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    assert_cairo_test_cases,
    CreateProtostarProjectFixture,
)
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_prank_cheatcode(protostar: ProtostarFixture):
    protostar.create_contracts({"pranked": CONTRACTS_PATH / "pranked.cairo"})

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "prank_cairo_cheatcode_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_not_fails_when_pranked",
            "test_not_fails_when_pranked_wrong_target",
        ],
        expected_failed_test_cases_names=[
            "test_fails_when_not_pranked",
            "test_fails_when_different_target_is_pranked",
        ],
    )
