from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from protostar.protostar_exception import ProtostarExceptionSilent

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


def calculate_skipped(
    total_count: int, broken_count: int, failed_count: int, passed_count: int
):
    return total_count - (broken_count + failed_count + passed_count)


# pylint: disable=too-many-instance-attributes
class TestingSummary:
    def __init__(self, test_results: List[TestResult], testing_seed: Seed) -> None:
        self.testing_seed = testing_seed
        self.test_results: List[TestResult] = []
        self.test_suites_mapping: Dict[Path, List[TestResult]] = defaultdict(list)
        self.passed: List[PassedTestCaseResult] = []
        self.failed: List[FailedTestCaseResult] = []
        self.broken: List[BrokenTestCaseResult] = []
        self.broken_suites: List[BrokenTestSuiteResult] = []
        self.skipped: List[SkippedTestCaseResult] = []
        self.extend(test_results)

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
                self.skipped.append(case_result)

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
