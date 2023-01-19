from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from protostar.protostar_exception import ProtostarExceptionSilent
from protostar.testing.test_collector import TestCollector

from .test_results import (
    BrokenTestCaseResult,
    BrokenTestSuiteResult,
    FailedTestCaseResult,
    PassedTestCaseResult,
    SkippedTestCaseResult,
    TestCaseResult,
    TestResult,
    TimedTestCaseResult,
)
from .testing_seed import Seed


def _calculate_skipped(
    total_count: int, broken_count: int, failed_count: int, passed_count: int
) -> int:
    return total_count - (broken_count + failed_count + passed_count)


# pylint: disable=too-many-instance-attributes
class TestingSummary:
    def __init__(
        self,
        initial_test_results: List[TestResult],
        testing_seed: Seed,
        test_collector_result: TestCollector.Result,
    ) -> None:
        self.test_collector_result = test_collector_result
        self.testing_seed = testing_seed
        self.test_results: List[TestResult] = []
        self.test_suites_mapping: Dict[Path, List[TestResult]] = defaultdict(list)
        self.passed: List[PassedTestCaseResult] = []
        self.failed: List[FailedTestCaseResult] = []
        self.broken: List[BrokenTestCaseResult] = []
        self.broken_suites: List[BrokenTestSuiteResult] = []
        self.explicitly_skipped: List[SkippedTestCaseResult] = []
        self.extend(initial_test_results)

    def extend(self, test_results: List[TestResult]):
        self.test_results += test_results
        for case_result in test_results:
            self.test_suites_mapping[case_result.file_path].append(case_result)

            if isinstance(case_result, PassedTestCaseResult):
                self.passed.append(case_result)
            if isinstance(case_result, FailedTestCaseResult):
                self.failed.append(case_result)
            if isinstance(case_result, BrokenTestCaseResult):
                self.broken.append(case_result)
            if isinstance(case_result, BrokenTestSuiteResult):
                self.broken_suites.append(case_result)
            if isinstance(case_result, SkippedTestCaseResult):
                self.explicitly_skipped.append(case_result)

    def get_skipped_test_cases_count(self) -> int:
        return _calculate_skipped(
            broken_count=len(self.broken),
            failed_count=len(self.failed),
            passed_count=len(self.passed),
            total_count=self.test_collector_result.test_cases_count,
        )

    def get_skipped_test_suites_count(self) -> int:
        failed_tests_paths = {str(item.file_path) for item in self.failed}
        passed_tests_paths = {str(item.file_path) for item in self.passed}
        passed_test_suites = failed_test_suites = 0
        for test_suite in self.test_collector_result.test_suites:
            if str(test_suite.test_path) in failed_tests_paths:
                failed_test_suites += 1
            elif str(test_suite.test_path) in passed_tests_paths:
                passed_test_suites += 1

        return _calculate_skipped(
            broken_count=len(self.broken_suites),
            failed_count=failed_test_suites,
            passed_count=passed_test_suites,
            total_count=len(self.test_collector_result.test_suites),
        )

    def assert_all_passed(self):
        if self.failed or self.broken_suites or self.broken:
            raise ProtostarExceptionSilent("Not all test cases passed")

    def get_slowest_test_cases_list(
        self,
        count: int,
    ) -> List[TimedTestCaseResult]:
        lst: List[TimedTestCaseResult]
        lst = self.passed + self.failed + self.broken  # type: ignore
        lst.sort(key=lambda x: x.execution_time, reverse=True)
        return lst[: min(count, len(lst))]

    def __getitem__(self, protostar_test_case_name: str):
        for test_result in self.test_results:
            if (
                isinstance(test_result, TestCaseResult)
                and test_result.test_case_name == protostar_test_case_name
            ):
                return test_result
        assert False, f"Couldn't find '{protostar_test_case_name}' test case result."
