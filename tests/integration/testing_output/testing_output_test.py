from pathlib import Path

import pytest

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

    for passed_test_case in testing_summary.passed:
        output = passed_test_case.display()
        assert "steps=" in output
        assert "pedersen_builtin=" in output
        assert "range_check=" not in output
