from pathlib import Path
from typing import Set
from types import MethodType

import pytest
from protostar.commands.test.testing_summary import TestingSummary
from protostar.utils.log_color_provider import LogColorProvider
from tests.integration.conftest import RunCairoTestRunnerFixture


def assert_exec_times_in_desc_order(logs: str) -> None:
    raw_exec_times = [row.split()[3] for row in logs.split("\n")]
    exec_times = [
        float(exec_time.lstrip("(time=").rstrip("s)")) for exec_time in raw_exec_times
    ]  # "(time={NUMBER}s)" -> {NUMBER}
    assert exec_times == sorted(exec_times, reverse=True)


def get_one_digit_test_indices(logs: str) -> Set[int]:
    # "{NUMBER}." -> {NUMBER}
    return set([int(row.split()[0][:-1]) for row in logs.split("\n")])


@pytest.fixture(name="testing_summary")
async def testing_summary_fixture(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
) -> TestingSummary:
    return await run_cairo_test_runner(
        Path(__file__).parent / "testing_timing_test.cairo"
    )


@pytest.fixture(name="no_color_log_color_provider")
def no_color_log_color_provider_fixture() -> LogColorProvider:
    no_color_log_color_provider = LogColorProvider()
    no_color_log_color_provider.colorize = MethodType(
        (lambda self, color, string: string), no_color_log_color_provider  # type: ignore
    )
    no_color_log_color_provider.bold = MethodType(
        (lambda self, string: string), no_color_log_color_provider  # type: ignore
    )
    return no_color_log_color_provider


async def test_timing_less_than_tests(
    testing_summary: TestingSummary, no_color_log_color_provider: LogColorProvider
):
    test3 = testing_summary._format_slow_test_cases_list(3, no_color_log_color_provider)
    assert_exec_times_in_desc_order(test3)
    assert {1, 2, 3} == get_one_digit_test_indices(test3)


async def test_timing_equal_to_the_number_of_tests(
    testing_summary: TestingSummary, no_color_log_color_provider: LogColorProvider
):
    test4 = testing_summary._format_slow_test_cases_list(4, no_color_log_color_provider)
    assert_exec_times_in_desc_order(test4)
    assert {1, 2, 3, 4} == get_one_digit_test_indices(test4)


async def test_timing_more_than_tests(
    testing_summary: TestingSummary, no_color_log_color_provider: LogColorProvider
):
    # Specyfing a number too big should have no effect, because of potential skipped tests.
    test5 = testing_summary._format_slow_test_cases_list(5, no_color_log_color_provider)
    assert_exec_times_in_desc_order(test5)
    assert {1, 2, 3, 4} == get_one_digit_test_indices(test5)


async def test_timing_zero(testing_summary: TestingSummary):
    # Zero should yield no result
    test0 = testing_summary._format_slow_test_cases_list(0)
    assert test0 == ""
