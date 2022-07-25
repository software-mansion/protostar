from pathlib import Path

import pytest

from tests.integration.conftest import (
    assert_cairo_test_cases,
    RunCairoTestRunnerFixture,
)


@pytest.mark.asyncio
async def test_basic(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_test.cairo", seed=10
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_fuzz",
        ],
        expected_failed_test_cases_names=[
            "test_fails_if_big",
        ],
    )


@pytest.mark.asyncio
async def test_non_felt_parameter(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "non_felt_parameter_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[],
        expected_broken_test_cases_names=["test_fails_on_non_felt_parameter"],
    )
