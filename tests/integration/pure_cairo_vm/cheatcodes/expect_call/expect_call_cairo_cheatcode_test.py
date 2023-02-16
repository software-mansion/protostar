from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import CONTRACTS_PATH


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_expect_call(protostar: ProtostarFixture):
    protostar.create_contracts(
        {
            "basic": CONTRACTS_PATH / "basic_with_multiple_args.cairo",
        }
    )
    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "expect_call_test.cairo", cairo_test_runner=True
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_expect_call_success",
        ],
        expected_failed_test_cases_names=[
            "test_expect_call_after_the_call",
            "test_expect_call_wrong_address",
            "test_expect_call_wrong_calldata",
            "test_expect_call_partial_fail",
            "test_expect_call_expected_but_not_found",
            "test_expect_call_wrong_function_called",
        ],
    )
