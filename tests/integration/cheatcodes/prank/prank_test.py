from pathlib import Path

import pytest

from src.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_prank_cheatcode(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).run(TestCommand.Args(target=Path(__file__).parent / "prank_test.cairo"))

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_remote_prank",
            "test_local_prank",
            "test_pranks_only_target",
            "test_syscall_counter_correct",
            "test_missing_remote_prank",
            "test_missing_local_prank",
            "test_prank_wrong_target",
        ],
        expected_failed_test_cases_names=[],
    )
