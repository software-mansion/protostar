import itertools
from pathlib import Path
from typing import List, Optional, Union
from enum import Enum
from sympy import O
from tqdm import tqdm as bar

from src.commands.test.cases import BrokenTest, FailedCase, PassedCase
from src.commands.test.utils import TestSubject

CaseResult = Union[PassedCase, FailedCase, BrokenTest]


class ResultReport(Enum):
    PASSED_CASE = 1
    FAILED_CASE = 2
    BROKEN_CASE = 3


class Reporter:
    def __init__(self, subject, queue):
        self.subject = subject
        self.reports_queue = queue
        self.broken_tests = []
        self.failed_cases = []
        self.passed_cases = []

    def report(self, subject: TestSubject, case_result: CaseResult):
        if isinstance(case_result, PassedCase):
            self.passed_cases.append(case_result)
            self.reports_queue.put((subject, ResultReport.PASSED_CASE))
        if isinstance(case_result, FailedCase):
            self.failed_cases.append(case_result)
            self.reports_queue.put((subject, ResultReport.FAILED_CASE))
        if isinstance(case_result, BrokenTest):
            self.broken_tests.append(case_result)
            self.reports_queue.put((subject, ResultReport.BROKEN_CASE))

    @property
    def passed_count(self):
        return len(self.passed_cases)

    @property
    def broken_count(self):
        return len(self.broken_tests)

    @property
    def failed_count(self):
        return len(self.failed_cases)


class ReportCollector:
    _collected_count: Optional[int]
    collected_subjects: List[TestSubject]
    tests_root: Path

    def __init__(self, tests_root: Path, test_subjects, queue):
        self.collected_subjects = test_subjects
        self.collected_count = sum(
            [len(subject.test_functions) for subject in self.collected_subjects]
        )
        self.tests_root = tests_root
        self.reports_queue = queue

    def report_collected(self):
        if self.collected_count:
            print(f"Collected {self.collected_count} items")
        else:
            print("No cases found")

    def live_reporting(self):
        self.report_collected()
        with bar(total=self.collected_count) as progress_bar:
            tests_left = self.collected_count
            while tests_left > 0:
                subject, report = self.reports_queue.get(block=True)
                if report == ResultReport.BROKEN_CASE:
                   tests_in_case = len(subject.test_functions)
                   progress_bar.update(tests_in_case)
                   tests_left -= tests_in_case
                else:
                    progress_bar.update(1)
                    tests_left -= 1
            

    def get_reporter(self, subject):
        return Reporter(subject, self.reports_queue)

    @staticmethod
    def report_collection_error():
        print("------- TEST COLLECTION ERROR -------")

    def report_summary(self, reporters):
        failed_tests_amt = sum([r.failed_count for r in reporters])
        succeeded_tests_amt = sum([r.passed_count for r in reporters])
        broken_tests_amt = sum([r.broken_count for r in reporters])

        ran_tests = succeeded_tests_amt + failed_tests_amt
        
        if failed_tests_amt > 0:
            self._report_failures(reporters)
        if broken_tests_amt > 0:
            self._report_broken_tests(reporters)

        print("\n----- TEST SUMMARY ------")
        if failed_tests_amt:
            print(f"{failed_tests_amt} failed, ", end="")
        if broken_tests_amt:
            print(f"{broken_tests_amt} failed to run, ", end="")

        print(f"{succeeded_tests_amt} passed")
        print(f"Ran {ran_tests} out of {self.collected_count} total tests")


    def _report_failures(self, reporters):

        print("\n------- FAILURES --------")
        for test_path, failed_cases in [
            (r.subject.test_path, r.failed_cases) for r in reporters
        ]:

            for failed_case in failed_cases:
                print(
                    f"{test_path.resolve().relative_to(self.tests_root.resolve())}::{failed_case.function_name}"
                )
                print(str(failed_case.exception))
                print("")

    def _report_broken_tests(self, reporters):

        print("\n----- BROKEN TESTS ------")
        for broken_subject in itertools.chain([r.broken_tests for r in reporters]):
            print(
                broken_subject.file_path.resolve().relative_to(
                    self.tests_root.resolve()
                )
            )
            print(str(broken_subject.exception))
            print("")
