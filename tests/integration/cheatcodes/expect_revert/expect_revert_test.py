from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.mark.asyncio
async def test_expect_revert(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "expect_revert_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_partial_error_message",
            "test_call_not_existing_contract_err_message",
            "test_call_not_existing_contract",
            "test_error_message",
            "test_with_except_revert",
        ],
        expected_failed_test_cases_names=[
            "test_error_was_not_raised_before_stopping_expect_revert_fail_expected",
            "test_call_not_existing_contract_fail_expected",
            "test_with_except_out_of_scope_revert_fail_expected",
            "test_with_except_revert_fail_expected",
            "test_fail_error_message",
        ],
    )


@pytest.fixture(autouse=True, scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_error_message_when_no_arguments_were_provided(
    protostar: ProtostarFixture,
):
    (_, formatted_test_result) = await protostar.run_test_case("%{ expect_revert() %}")

    assert "matching the following error" not in formatted_test_result
    assert "Expected revert" in formatted_test_result


async def test_already_expecting_error_message_when_no_arguments_were_provided(
    protostar: ProtostarFixture,
):
    (_, formatted_test_result) = await protostar.run_test_case(
        """
        %{
            expect_revert()
            expect_revert()
        %}
        """
    )

    assert "matching the following error" not in formatted_test_result
    assert "Protostar is already expecting an exception" in formatted_test_result
