from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_other_cheatcodes(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/test_other_cheatcodes.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_roll_cheat",
            "test_warp_cheat",
            "test_start_stop_prank_cheat",
            "test_mock_call_returning_felt",
            "test_mock_call_returning_array",
            "test_mock_call_returning_struct",
            "test_clearing_mocks",
            "test_deploy_contract",
            "test_deploy_contract_with_args_in_constructor",
            "test_call_not_existing_contract",
            "test_call_not_existing_contract_specific_error",
        ],
        expected_failed_test_cases_names=[
            "test_cannot_freeze_when_cheatcode_exception_is_raised"
        ],
    )
