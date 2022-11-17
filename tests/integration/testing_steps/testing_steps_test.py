from pathlib import Path

import pytest

from protostar.commands.test.test_result_formatter import format_test_result
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_testing_steps(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "testing_steps_test.cairo", max_steps=10
    )

    assert_cairo_test_cases(
        testing_summary, expected_failed_test_cases_names=["test_max_steps"]
    )

    assert "OUT_OF_RESOURCES" in format_test_result(testing_summary.failed[0])

    ###

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "testing_steps_test.cairo", max_steps=-1
    )

    assert_cairo_test_cases(
        testing_summary, expected_passed_test_cases_names=["test_max_steps"]
    )

    ###

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "testing_steps_test.cairo", max_steps=1000
    )

    assert_cairo_test_cases(
        testing_summary, expected_passed_test_cases_names=["test_max_steps"]
    )
