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
            "test_reflect_passed_full_assert",
        ],
        expected_failed_test_cases_names=[
            "test_reflect_failed_assert",
            "test_reflect_failed_corruption",
        ],
    )

    long_failed = (
        testing_summary.failed[0]
        if "captured stdout" in testing_summary.failed[0].display()
        else testing_summary.failed[1]
    )

    print(long_failed.display())

    assert "AssertionError" + str(long_failed.exception)
    assert "VoterInfo" in long_failed.display()
    assert "a=Struct1(" in long_failed.display()
