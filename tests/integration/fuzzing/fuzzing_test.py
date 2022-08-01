from pathlib import Path

import pytest

from tests.integration.conftest import (
    assert_cairo_test_cases,
    RunCairoTestRunnerFixture,
)


@pytest.mark.asyncio
async def test_basic(run_cairo_test_runner: RunCairoTestRunnerFixture):
    seed = 10

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_test.cairo", seed=seed
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

    assert testing_summary.testing_seed.value == seed
    assert testing_summary.testing_seed.was_used


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


@pytest.mark.asyncio
async def test_state_is_isolated(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "state_isolation_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_storage_var",
        ],
        expected_failed_test_cases_names=[],
    )


@pytest.mark.asyncio
async def test_hypothesis_multiple_errors(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    """
    This test potentially raises ``hypothesis.errors.MultipleFailures``
    when ``report_multiple_bugs`` setting is set to ``True``.
    """

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "hypothesis_multiple_errors_test.cairo", seed=10
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[
            "test_hypothesis_multiple_errors",
        ],
    )
