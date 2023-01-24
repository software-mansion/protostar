from typing import Optional

from protostar.testing.testing_summary import TestingSummary

from .cairo_test_results_data import CairoTestResultsData
from .cairo_test_results_diff_generator import CairoTestCasesDiffGenerator


def assert_cairo_test_cases(
    testing_summary: TestingSummary,
    expected_passed_test_cases_names: Optional[list[str]] = None,
    expected_failed_test_cases_names: Optional[list[str]] = None,
    expected_broken_test_cases_names: Optional[list[str]] = None,
    expected_skipped_test_cases_names: Optional[list[str]] = None,  # Explicitly skipped
):
    expected_passed_test_cases_names = expected_passed_test_cases_names or []
    expected_failed_test_cases_names = expected_failed_test_cases_names or []
    expected_broken_test_cases_names = expected_broken_test_cases_names or []
    expected_skipped_test_cases_names = expected_skipped_test_cases_names or []

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

    actual = CairoTestResultsData(
        passed=passed_test_cases_names,
        failed=failed_test_cases_names,
        broken=broken_test_cases_names,
        skipped=skipped_test_cases_names,
    )

    expected = CairoTestResultsData(
        passed=set(expected_passed_test_cases_names),
        failed=set(expected_failed_test_cases_names),
        broken=set(expected_broken_test_cases_names),
        skipped=set(expected_skipped_test_cases_names),
    )

    diff = CairoTestCasesDiffGenerator.from_testing_summary(testing_summary).execute(
        actual, expected
    )
    if diff:
        # diff is not included in the condition to improve errors' readability
        assert False, diff
    assert actual == expected
