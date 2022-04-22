from collections import defaultdict
from pathlib import Path
from tkinter import W
from typing import Dict, List, Optional, Union
from black import Enum
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

class TestReporter:
    _collected_count: Optional[int]
    collected_subjects: List[TestSubject]
    tests_root: Path

    def __init__(self, tests_root: Path, test_subjects, queue):
        self.collected_subjects = test_subjects
        self.collected_count = sum([len(subject.test_functions) for subject in self.collected_subjects])
        self.tests_root = tests_root
        self.reports_queue = queue

    
    # def get_collected_results(self):
    #     return self.passed_cases + self.failed_cases + self.broken_tests

    def report_collected(self):
        if self.collected_count:
            print(f"Collected {self.collected_count} items")
        else:
            print("No cases found")

    def live_reporting(self):
        self.report_collected()
        # for _ in bar(range(self.collected_count)):
        #     _, _ = self.reports_queue.get(block=True)

   
    def get_reporter(self, subject):
        return Reporter(subject, self.reports_queue)

    @staticmethod
    def report_collection_error():
        print("!!!!!!!!!! TEST COLLECTION ERROR !!!!!!!!!!")

    def report_summary(self, reporters):
        breakpoint()
        

        failed_tests_amt = sum([r.failed_count for r in reporters])
        succeeded_tests_amt = sum([r.passed_count for r in reporters])
        broken_tests_amt = sum([r.broken_count for r in reporters])

        ran_tests = succeeded_tests_amt + failed_tests_amt

        print("\n----- TEST SUMMARY ------")
        if failed_tests_amt:
            print(f"{failed_tests_amt} failed, ", end="")
        if broken_tests_amt:
            print(f"{broken_tests_amt} failed to run, ", end="")

        print(f"{succeeded_tests_amt} passed")
        print(f"Ran {ran_tests} out of {self.collected_count} total tests")

    #     self._report_failures()

    # def _report_failures(self, reporters):
    #     if self.failed_cases:
    #         print("\n------- FAILURES --------")
    #         for test_path, failed_cases in self.failed_tests_by_subject.items():

    #             for failed_case in failed_cases:
    #                 print(
    #                     f"{test_path.resolve().relative_to(self.tests_root.resolve())}::{failed_case.function_name}"
    #                 )
    #                 print(str(failed_case.exception))
    #                 print("")
    #     if self.broken_tests:
    #         print("\n----- BROKEN TESTS ------")
    #         for broken_subject in self.broken_tests:
    #             print(
    #                 broken_subject.file_path.resolve().relative_to(
    #                     self.tests_root.resolve()
    #                 )
    #             )
    #             print(str(broken_subject.exception))
    #             print("")

