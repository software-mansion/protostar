from pathlib import Path

from protostar.commands.test.test_result_formatter import format_test_result
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
        output = format_test_result(passed_test_case)
        assert "steps=" in output
        assert "pedersen_builtin=" in output
        assert "range_check=" not in output
