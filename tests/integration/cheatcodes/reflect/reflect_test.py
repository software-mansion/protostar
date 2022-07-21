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
            "test_reflect_passed_simple",
            "test_reflect_passed_pointer",
            "test_reflect_passed_pointer_loop",
            "test_reflect_passed_type_pointer",
            "test_reflect_passed_repr",
            "test_reflect_passed_full",
        ],
        expected_failed_test_cases_names=[
            "test_reflect_failed_simple",
            "test_reflect_failed_corruption",
            "test_reflect_failed_illegal_arg",
            "test_reflect_failed_getattr_felt",
            "test_reflect_failed_getattr_pointer",
            "test_reflect_failed_invalid_member",
            "test_reflect_failed_get_on_none",
        ],
    )
