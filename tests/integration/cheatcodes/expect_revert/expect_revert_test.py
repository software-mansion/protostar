from pathlib import Path

import pytest

from src.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_expect_revert(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).run(TestCommand.Args(target=Path(__file__).parent / "expect_revert_test.cairo"))

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
