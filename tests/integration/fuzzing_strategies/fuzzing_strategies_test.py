from pathlib import Path

from protostar.commands.test.test_results import PassedFuzzTestCaseResult
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_integers(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "integers_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_integers"],
        expected_failed_test_cases_names=[],
    )

    for result in testing_summary.passed:
        assert isinstance(result, PassedFuzzTestCaseResult)
        assert result.fuzz_runs_count == 5


async def test_integers_unbounded(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "integers_unbounded_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=["test_integers_unbounded"],
    )


async def test_flaky_strategy(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "flaky_strategy_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[
            "test_flaky_strategy",
        ],
    )


async def test_multiple_learning_steps(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "multiple_learning_steps_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_multiple_learning_steps"],
        expected_failed_test_cases_names=[],
    )


async def test_invalid_calls(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "invalid_calls_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[
            "test_integers_inverted_range",
            "test_not_strategy_object",
            "test_unknown_parameter",
        ],
    )
