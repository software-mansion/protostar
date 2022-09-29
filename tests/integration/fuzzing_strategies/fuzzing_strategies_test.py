from pathlib import Path

import pytest

from protostar.testing.test_results import PassedFuzzTestCaseResult
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


async def test_felts(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "felts_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_rc_bound"],
    )


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
        expected_broken_test_cases_names=[
            "test_unknown_parameter",
            "test_integers_inverted_range",
            "test_not_strategy_object",
            "test_repeated_parameter",
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
            "test_chaining",
            "test_filtering",
            "test_mapping",
        ],
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
            "test_one_of_filtering",
            "test_one_of_mapping_and_filtering",
        ],
        expected_failed_test_cases_names=[],
    )


async def test_short_strings(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "short_strings_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_correct_short_string"],
        expected_failed_test_cases_names=[],
    )
