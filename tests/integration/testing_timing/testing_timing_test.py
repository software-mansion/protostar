from pathlib import Path
from typing import Set

import pytest

from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


def assert_in_order(logs: str) -> None:
    raw_exec_times = [row.split()[3] for row in logs.split("\n")]
    exec_times = [
        float(exec_time[exec_time.find(".") -1 : exec_time.find(".") + 3])
        for exec_time in raw_exec_times
    ] # decoloring
    assert exec_times == sorted(exec_times, reverse=True)


def get_one_digit_test_indices(logs: str) -> Set[int]:
    raw_indices = [row.split()[0] for row in logs.split("\n")]
    return set(
        int(index[index.find("m") + 1 : index.find("m") + 2]) for index in raw_indices
    )  # decoloring


async def test_testing_output(run_cairo_test_runner: RunCairoTestRunnerFixture):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "testing_timing_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_passed_sleep",
            "test_passed_simple",
        ],
        expected_failed_test_cases_names=[
            "test_failed_sleep",
            "test_failed_simple",
        ],
    )

    test3 = testing_summary._format_slow_test_cases_list(3)
    assert_in_order(test3)
    indices3 = get_one_digit_test_indices(test3)
    assert {1, 2, 3} == indices3

    test4 = testing_summary._format_slow_test_cases_list(4)
    assert_in_order(test4)
    assert {1, 2, 3, 4} == get_one_digit_test_indices(test4)

    # Specyfing a number too big should have no effect, because of potential skipped tests.
    test5 = testing_summary._format_slow_test_cases_list(5)
    assert_in_order(test5)
    assert {1, 2, 3, 4} == get_one_digit_test_indices(test5)

    # Zero should yield no result
    test0 = testing_summary._format_slow_test_cases_list(0)
    assert test0 == ""
