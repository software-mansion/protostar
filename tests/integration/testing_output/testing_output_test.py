from pathlib import Path

import pytest

from protostar.commands.test.test_result_formatter import TestResultFormatter
from protostar.utils.log_color_provider import LogColorProvider
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.mark.asyncio
async def test_testing_output(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "testing_output_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_printing_resource_usage_in_unit_testing_approach",
            "test_printing_resource_usage_in_integration_testing_approach",
        ],
        expected_failed_test_cases_names=[],
    )

    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    test_result_formatter = TestResultFormatter(log_color_provider=log_color_provider)

    for passed_test_case in testing_summary.passed:
        output = test_result_formatter.format(passed_test_case)
        assert "steps=" in output
        assert "pedersen_builtin=" in output
        assert "range_check=" not in output
