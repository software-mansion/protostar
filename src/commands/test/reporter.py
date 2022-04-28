import queue
from logging import Logger
from pathlib import Path

# pylint: disable=unused-import
from typing import List, Tuple

from tqdm import tqdm as bar

from src.commands.test.cases import BrokenTest, CaseResult, FailedCase, PassedCase
from src.commands.test.utils import TestSubject


class Reporter:
    def __init__(self, live_reports_queue: queue.Queue):
        self.live_reports_queue = live_reports_queue
        self.test_case_results: List[CaseResult] = []

    def report(self, subject: TestSubject, case_result: CaseResult):
        self.live_reports_queue.put((subject, case_result))
        self.test_case_results.append(case_result)


class CaseResults:
    def __init__(self, case_results: List[CaseResult]) -> None:
        self.case_results = case_results
        self.passed: List[PassedCase] = []
        self.failed: List[FailedCase] = []
        self.broken: List[BrokenTest] = []

        for case_result in case_results:
            if isinstance(case_result, PassedCase):
                self.passed.append(case_result)
            if isinstance(case_result, FailedCase):
                self.failed.append(case_result)
            if isinstance(case_result, BrokenTest):
                self.broken.append(case_result)


class ReporterCoordinator:
    def __init__(
        self,
        tests_root: Path,
        test_subjects: List[TestSubject],
        live_reports_queue: "queue.Queue[Tuple[TestSubject, CaseResult]]",
        logger: Logger,
    ):
        self.collected_subjects = test_subjects
        self.collected_count = sum(
            [len(subject.test_functions) for subject in self.collected_subjects]
        )
        self.tests_root = tests_root
        self.live_reports_queue = live_reports_queue
        self.logger = logger

    def report_collected(self):
        if self.collected_count:
            self.logger.info(f"Collected {self.collected_count} items")
        else:
            self.logger.warn("No cases found")

    def live_reporting(self):
        self.report_collected()
        try:
            with bar(total=self.collected_count) as progress_bar:
                tests_left_n = self.collected_count
                while tests_left_n > 0:
                    subject, case_result = self.live_reports_queue.get(
                        block=True, timeout=1000
                    )

                    progress_bar.write(str(case_result))

                    if isinstance(case_result, BrokenTest):
                        tests_in_case_count = len(subject.test_functions)
                        progress_bar.update(tests_in_case_count)
                        tests_left_n -= tests_in_case_count
                    else:
                        progress_bar.update(1)
                        tests_left_n -= 1
        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass

    def create_reporter(self):
        return Reporter(self.live_reports_queue)

    @staticmethod
    def report_collection_error():
        print("------- TEST COLLECTION ERROR -------")

    def report_summary(self, reporters: List[Reporter]):
        test_case_results = CaseResults(
            sum([r.test_case_results for r in reporters], [])
        )

        failed_test_cases_amt = len(test_case_results.failed)
        passed_test_cases_amt = len(test_case_results.passed)
        broken_tests_amt = len(test_case_results.broken)

        ran_tests_count = passed_test_cases_amt + failed_test_cases_amt

        if failed_test_cases_amt > 0:
            self._report_failures(test_case_results.failed)
        if broken_tests_amt > 0:
            self._report_broken_tests(test_case_results.broken)

        print("\n----- TEST SUMMARY ------")
        if failed_test_cases_amt:
            print(f"{failed_test_cases_amt} failed, ", end="")
        if broken_tests_amt:
            print(f"{broken_tests_amt} failed to run, ", end="")

        print(f"{passed_test_cases_amt} passed")
        print(f"Ran {ran_tests_count} out of {self.collected_count} total tests")

    def _report_failures(self, failed_cases: List[FailedCase]):

        print("\n------- FAILURES --------")
        for failed_case in failed_cases:
            print(
                f"{failed_case.file_path.resolve().relative_to(self.tests_root.resolve())}::{failed_case.function_name}"
            )
            print(str(failed_case.exception))
            print("")

    def _report_broken_tests(self, broken_tests: List[BrokenTest]):

        print("\n----- BROKEN TESTS ------")
        for broken_test in broken_tests:
            print(
                broken_test.file_path.resolve().relative_to(self.tests_root.resolve())
            )
            print(str(broken_test.exception))
            print("")
