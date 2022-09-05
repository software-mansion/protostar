from pathlib import Path

import pytest

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


@pytest.mark.skip("https://github.com/software-mansion/protostar/issues/711")
async def test_edge_cases(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "edge_cases_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_multiple_given_calls",
        ],
        expected_failed_test_cases_names=[
            "test_integers_inverted_range",
            "test_not_strategy_object",
            "test_repeated_parameter",
        ],
        expected_broken_test_cases_names=[
            "test_unknown_parameter",
        ],
    )


async def test_mapping_and_filtering(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "map_and_filter_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_filtering",
            "test_mapping",
        ],
        expected_failed_test_cases_names=["test_chaining"],
    )


async def test_one_of(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "one_of_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_one_of",
        ],
        expected_failed_test_cases_names=[],
    )
