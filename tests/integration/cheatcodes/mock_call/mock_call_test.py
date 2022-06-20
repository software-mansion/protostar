from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_prank_cheatcode(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[str(Path(__file__).parent / "mock_call_test.cairo")])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_remote_mock",
            "test_local_mock",
            "test_missing_remote_mock",
            "test_missing_local_mock",
            "test_syscall_counter_updated",
            "test_mock_call_wrong_target",
            "test_mock_call_wrong_selector_target",
            "test_library_call_not_affected_by_mock",
        ],
        expected_failed_test_cases_names=["test_mock_call_twice"],
    )
