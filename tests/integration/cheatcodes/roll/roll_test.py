from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_roll_cheatcode(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/roll_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_changing_block_number",
        ],
        expected_failed_test_cases_names=[],
    )
