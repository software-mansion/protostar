from typing import Optional

from protostar.testing.testing_summary import TestingSummary

from .cairo_test_results_data import CairoTestResultsData
from .cairo_test_results_diff_generator import CairoTestCasesDiffGenerator


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: Optional[list[str]] = None,
    expected_failed_test_cases_names: Optional[list[str]] = None,
    expected_broken_test_cases_names: Optional[list[str]] = None,
    expected_skipped_test_cases_names: Optional[list[str]] = None,
):
    actual_test_results_data = convert_testing_summary_to_test_results_data(
        testing_summary
    )
    expected_test_results_data = CairoTestResultsData(
        passed=set(expected_passed_test_cases_names or []),
        failed=set(expected_failed_test_cases_names or []),
        broken=set(expected_broken_test_cases_names or []),
        skipped=set(expected_skipped_test_cases_names or []),
    )
    diff = CairoTestCasesDiffGenerator.from_testing_summary(testing_summary).execute(
        actual_test_results_data=actual_test_results_data,
        expected_test_results_data=expected_test_results_data,
    )
    if diff:
        # diff is not included in the condition to improve errors' readability
        assert False, diff
    assert actual_test_results_data == expected_test_results_data  # safety net


def convert_testing_summary_to_test_results_data(
    testing_summary: TestingSummary,
) -> CairoTestResultsData:
    passed_test_cases_names = set(
        passed_test_case.test_case_name for passed_test_case in testing_summary.passed
    )
    failed_test_cases_names = set(
        failed_test_case.test_case_name for failed_test_case in testing_summary.failed
    )
    broken_test_cases_names = set(
        broken_test_case.test_case_name for broken_test_case in testing_summary.broken
    )
    skipped_test_cases_names = set(
        skipped_test_case.test_case_name
        for skipped_test_case in testing_summary.explicitly_skipped
    )
    for broken_test_case in testing_summary.broken_suites:
        for test_case_name in broken_test_case.test_case_names:
            broken_test_cases_names.add(test_case_name)
    return CairoTestResultsData(
        passed=passed_test_cases_names,
        failed=failed_test_cases_names,
        broken=broken_test_cases_names,
        skipped=skipped_test_cases_names,
    )
