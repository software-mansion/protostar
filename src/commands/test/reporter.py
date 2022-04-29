import queue
from logging import Logger
from pathlib import Path

# pylint: disable=unused-import
from typing import Any, Dict, List, Tuple, cast

from tqdm import tqdm as bar

from src.commands.test.cases import BrokenTest, CaseResult, FailedCase, PassedCase
from src.commands.test.utils import TestSubject
from src.utils.log_color_provider import log_color_provider


class Reporter:
    def __init__(self, live_reports_queue: queue.Queue):
        self.live_reports_queue = live_reports_queue
        self.test_case_results: List[CaseResult] = []

    def report(self, subject: TestSubject, case_result: CaseResult):
        self.live_reports_queue.put((subject, case_result))
        self.test_case_results.append(case_result)


class TestingResult:
    @classmethod
    def from_reporters(cls, reporters: List[Reporter]) -> "TestingResult":
        return cls(sum([r.test_case_results for r in reporters], []))

    def __init__(self, case_results: List[CaseResult]) -> None:
        self.case_results = []
        self.test_files: Dict[Path, List[CaseResult]] = {}
        self.passed: List[PassedCase] = []
        self.failed: List[FailedCase] = []
        self.broken: List[BrokenTest] = []
        self.append(case_results)

    def append(self, case_results: List[CaseResult]):
        self.case_results += case_results
        for case_result in case_results:
            if case_result.file_path not in self.test_files:
                self.test_files[case_result.file_path] = []
            self.test_files[case_result.file_path].append(case_result)

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

        self.collected_tests_count = sum(
            [len(subject.test_functions) for subject in self.collected_subjects]
        )
        self.tests_root = tests_root
        self.live_reports_queue = live_reports_queue
        self.logger = logger

    def report_collected(self):
        if self.collected_tests_count:
            result: List[str] = ["Collected"]
            suits_count = len(self.collected_subjects)
            if suits_count == 1:
                result.append("1 suit")
            else:
                result.append(f"{suits_count} suits")

            result.append(", and")
            if self.collected_tests_count == 1:
                result.append("1 test")
            else:
                result.append(f"{self.collected_tests_count} tests")

            self.logger.info(
                f"Collected {len(self.collected_subjects)} suits, and {self.collected_tests_count} tests"
            )
        else:
            self.logger.warn("No cases found")

    def live_reporting(self):
        self.report_collected()
        testing_result = TestingResult([])

        try:
            with bar(
                total=self.collected_tests_count,
                bar_format="{l_bar}{bar}[{n_fmt}/{total_fmt}]",
                dynamic_ncols=True,
            ) as progress_bar:
                tests_left_n = self.collected_tests_count
                progress_bar.update()
                try:
                    while tests_left_n > 0:
                        subject, case_result = self.live_reports_queue.get(
                            block=True, timeout=1000
                        )
                        testing_result.append([case_result])
                        cast(Any, progress_bar).colour = (
                            "RED"
                            if len(testing_result.failed) + len(testing_result.broken)
                            > 0
                            else "GREEN"
                        )
                        progress_bar.write(str(case_result))

                        if isinstance(case_result, BrokenTest):
                            tests_in_case_count = len(subject.test_functions)
                            progress_bar.update(tests_in_case_count)
                            tests_left_n -= tests_in_case_count
                        else:
                            progress_bar.update(1)
                            tests_left_n -= 1
                finally:
                    progress_bar.bar_format = "{desc}"
                    progress_bar.update()
                    self.report_summary(testing_result)

        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass

    def create_reporter(self):
        return Reporter(self.live_reports_queue)

    def report_summary(self, testing_result: TestingResult):

        self.logger.info(
            log_color_provider.bold("Test suits: ")
            + self._get_test_suits_summary(testing_result)
        )
        self.logger.info(
            log_color_provider.bold("Tests:      ")
            + self._get_test_cases_summary(testing_result)
        )

    def _get_test_cases_summary(self, testing_result: TestingResult) -> str:
        failed_test_cases_amt = len(testing_result.failed)
        passed_test_cases_amt = len(testing_result.passed)

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                failed_count=failed_test_cases_amt,
                passed_count=passed_test_cases_amt,
                total_count=self.collected_tests_count,
            )
        )

    def _get_test_suits_summary(self, testing_result: TestingResult) -> str:
        passed_test_suits_amt = 0
        failed_test_suits_amt = 0
        broken_test_suits_amt = 0
        total_test_suits_amt = len(testing_result.test_files)
        for suit_case_results in testing_result.test_files.values():
            partial_results = TestingResult(suit_case_results)

            if len(partial_results.broken) > 0:
                broken_test_suits_amt += 1
                continue

            if len(partial_results.failed) > 0:
                failed_test_suits_amt += 1
                continue

            if len(partial_results.passed) > 0:
                passed_test_suits_amt += 1

        test_suits_result: List[str] = []

        if broken_test_suits_amt > 0:
            test_suits_result.append(
                log_color_provider.colorize("RED", f"{broken_test_suits_amt} broken")
            )
        if failed_test_suits_amt > 0:
            test_suits_result.append(
                log_color_provider.colorize("RED", f"{failed_test_suits_amt} failed")
            )
        if passed_test_suits_amt > 0:
            test_suits_result.append(
                log_color_provider.colorize("GREEN", f"{passed_test_suits_amt} passed")
            )
        if total_test_suits_amt > 0:
            test_suits_result.append(f"{total_test_suits_amt} total")

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                broken_count=broken_test_suits_amt,
                failed_count=failed_test_suits_amt,
                passed_count=passed_test_suits_amt,
                total_count=len(self.collected_subjects),
            )
        )

    # pylint: disable=no-self-use
    def _get_preprocessed_core_testing_summary(
        self,
        broken_count: int = 0,
        failed_count: int = 0,
        passed_count: int = 0,
        total_count: int = 0,
    ) -> List[str]:
        skipped_count = total_count - (broken_count + failed_count + passed_count)
        test_suits_result: List[str] = []

        if broken_count > 0:
            test_suits_result.append(
                log_color_provider.colorize("RED", f"{broken_count} broken")
            )
        if failed_count > 0:
            test_suits_result.append(
                log_color_provider.colorize("RED", f"{failed_count} failed")
            )
        if skipped_count > 0:
            test_suits_result.append(
                log_color_provider.colorize("YELLOW", f"{skipped_count} skipped")
            )
        if passed_count > 0:
            test_suits_result.append(
                log_color_provider.colorize("GREEN", f"{passed_count} passed")
            )
        if total_count > 0:
            test_suits_result.append(f"{total_count} total")

        return test_suits_result
