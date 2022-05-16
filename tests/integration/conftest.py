# pylint: disable=invalid-name
from typing import List

from protostar.commands.test.testing_summary import TestingSummary


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: List[str],
    expected_failed_test_cases_names: List[str],
):

    passed_test_cases_names = [
        passed_test_case.function_name for passed_test_case in testing_summary.passed
    ]
    failed_test_cases_names = [
        failed_test_case.function_name for failed_test_case in testing_summary.failed
    ]
    assert set(expected_passed_test_cases_names) == set(passed_test_cases_names)
    assert set(expected_failed_test_cases_names) == set(failed_test_cases_names)
    assert len(testing_summary.broken) == 0
