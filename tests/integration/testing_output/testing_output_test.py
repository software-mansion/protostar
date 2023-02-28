from pathlib import Path

from protostar.commands.cairo0.test import format_test_result
from protostar.io.log_color_provider import log_color_provider

from tests.integration.conftest import (
    RunTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_testing_output(
    run_test_runner: RunTestRunnerFixture,
):
    testing_summary = await run_test_runner(
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

    for passed_test_case in testing_summary.passed:
        output = format_test_result(passed_test_case).format_human(
            fmt=log_color_provider
        )
        assert "steps=" in output
        assert "pedersen_builtin=" in output
        assert "range_check=" not in output
