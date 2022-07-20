from pathlib import Path

import pytest

from protostar.commands.test.test_command import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_testing_output(mocker):
    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=mocker.MagicMock(),
    ).test(targets=[f"{Path(__file__).parent}/testing_output_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_printing_resource_usage_in_unit_testing_approach",
            "test_printing_resource_usage_in_integration_testing_approach",
        ],
        expected_failed_test_cases_names=[],
    )

    for passed_test_case in testing_summary.passed:
        output = passed_test_case.format()
        assert "steps=" in output
        assert "pedersen_builtin=" in output
        assert "range_check=" not in output
