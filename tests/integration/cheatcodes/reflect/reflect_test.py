from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_reflect_cheatcode(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/reflect_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_reflect_passed_assert",
            "test_reflect_passed_assert_pointer",
            "test_reflect_passed_pointer_loop",
        ],
        expected_failed_test_cases_names=[
            "test_reflect_failed_assert",
            "test_reflect_failed_corruption",
        ],
    )

    assert "AssertionError" + str(testing_summary.failed[0].exception)
    assert "VoterInfo" in testing_summary.failed[0].display()
    assert "a=Struct1(" in testing_summary.failed[0].display()
