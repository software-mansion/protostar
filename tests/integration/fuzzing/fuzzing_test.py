from pathlib import Path

from protostar.commands.test.test_cases import PassedFuzzTestCaseResult
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


async def test_basic(run_cairo_test_runner: RunCairoTestRunnerFixture):
    seed = 10

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_test.cairo",
        seed=seed,
        fuzz_max_examples=25,
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


async def test_state_is_isolated(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "state_isolation_test.cairo", fuzz_max_examples=5
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_storage_var",
        ],
        expected_failed_test_cases_names=[],
    )


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


async def test_max_fuzz_runs_less_or_equal_than_specified(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    fuzz_max_examples = 10

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "basic_test.cairo",
        seed=3,
        fuzz_max_examples=fuzz_max_examples,
    )

    assert isinstance(testing_summary.passed[0], PassedFuzzTestCaseResult)
    assert testing_summary.passed[0].fuzz_runs_count is not None
    assert testing_summary.passed[0].fuzz_runs_count <= fuzz_max_examples


async def test_strategies(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    fuzz_max_examples = 100

    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "strategies_test.cairo",
        fuzz_max_examples=fuzz_max_examples,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_integers",
            "test_integers_unbounded",
            "test_multiple_learning_steps",
        ],
        expected_failed_test_cases_names=[
            "test_flaky_strategies",
            "test_integers_inverted_range",
            "test_not_strategy_object",
            "test_unknown_parameter",
        ],
        expected_broken_test_cases_names=[],
    )

    for result in testing_summary.passed:
        assert isinstance(result, PassedFuzzTestCaseResult)
        assert result.fuzz_runs_count == fuzz_max_examples


async def test_issue_590(run_cairo_test_runner: RunCairoTestRunnerFixture):
    """
    https://github.com/software-mansion/protostar/issues/590
    """
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "issue_590_test.cairo",
        fuzz_max_examples=60,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=["test_590"],
    )
