import queue
from collections import defaultdict
from logging import Logger
from pathlib import Path

# pylint: disable=unused-import
from typing import Any, Dict, List, Tuple, cast

from tqdm import tqdm as bar

from src.commands.test.cases import BrokenTest, CaseResult, FailedCase, PassedCase
from src.commands.test.utils import TestSubject
from src.utils.log_color_provider import log_color_provider


class Reporter:
    def __init__(self, live_reports_queue: "ReporterCoordinator.Queue"):
        self.live_reports_queue = live_reports_queue

    def report(self, subject: TestSubject, case_result: CaseResult):
        self.live_reports_queue.enqueue((subject, case_result))


class TestingSummary:
    def __init__(self, case_results: List[CaseResult]) -> None:
        self.case_results = []
        self.test_files: Dict[Path, List[CaseResult]] = defaultdict(list)
        self.passed: List[PassedCase] = []
        self.failed: List[FailedCase] = []
        self.broken: List[BrokenTest] = []
        self.extend(case_results)

    def extend(self, case_results: List[CaseResult]):
        self.case_results += case_results
        for case_result in case_results:
            self.test_files[case_result.file_path].append(case_result)

            if isinstance(case_result, PassedCase):
                self.passed.append(case_result)
            if isinstance(case_result, FailedCase):
                self.failed.append(case_result)
            if isinstance(case_result, BrokenTest):
                self.broken.append(case_result)


class ReporterCoordinator:
    class Queue:
        def __init__(
            self, shared_queue: "queue.Queue[Tuple[TestSubject, CaseResult]]"
        ) -> None:
            self._shared_queue = shared_queue

        def dequeue(self) -> Tuple[TestSubject, CaseResult]:
            return self._shared_queue.get(block=True, timeout=1000)

        def enqueue(self, item: Tuple[TestSubject, CaseResult]) -> None:
            self._shared_queue.put(item)

    def __init__(
        self,
        tests_root: Path,
        test_subjects: List[TestSubject],
        logger: Logger,
    ):
        self.collected_subjects = test_subjects

        self.collected_tests_count = sum(
            [len(subject.test_functions) for subject in self.collected_subjects]
        )
        self.tests_root = tests_root
        self.logger = logger

    def report_collected(self):
        if self.collected_tests_count:
            result: List[str] = ["Collected"]
            suits_count = len(self.collected_subjects)
            if suits_count == 1:
                result.append("1 suit,")
            else:
                result.append(f"{suits_count} suits,")

            result.append("and")
            if self.collected_tests_count == 1:
                result.append("1 test case")
            else:
                result.append(f"{self.collected_tests_count} test cases")

            self.logger.info(" ".join(result))
        else:
            self.logger.warn("No cases found")

    def live_reporting(
        self,
        live_reports_queue: "ReporterCoordinator.Queue",
    ):
        self.report_collected()
        testing_summary = TestingSummary([])

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
                        (subject, case_result) = live_reports_queue.dequeue()
                        testing_summary.extend([case_result])
                        cast(Any, progress_bar).colour = (
                            "RED"
                            if len(testing_summary.failed) + len(testing_summary.broken)
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
                    self.report_summary(testing_summary)

        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass

    def create_reporter(self, live_reports_queue: "ReporterCoordinator.Queue"):
        return Reporter(live_reports_queue)

    def report_summary(self, testing_summary: TestingSummary):

        self.logger.info(
            log_color_provider.bold("Test suits: ")
            + self._get_test_suits_summary(testing_summary)
        )
        self.logger.info(
            log_color_provider.bold("Tests:      ")
            + self._get_test_cases_summary(testing_summary)
        )

    def _get_test_cases_summary(self, testing_result: TestingSummary) -> str:
        failed_test_cases_count = len(testing_result.failed)
        passed_test_cases_count = len(testing_result.passed)

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                failed_count=failed_test_cases_count,
                passed_count=passed_test_cases_count,
                total_count=self.collected_tests_count,
            )
        )

    def _get_test_suits_summary(self, testing_summary: TestingSummary) -> str:
        passed_test_suits_count = 0
        failed_test_suits_count = 0
        broken_test_suits_count = 0
        total_test_suits_count = len(testing_summary.test_files)
        for suit_case_results in testing_summary.test_files.values():
            partial_summary = TestingSummary(suit_case_results)

            if len(partial_summary.broken) > 0:
                broken_test_suits_count += 1
                continue

            if len(partial_summary.failed) > 0:
                failed_test_suits_count += 1
                continue

            if len(partial_summary.passed) > 0:
                passed_test_suits_count += 1

        test_suits_result: List[str] = []

        if broken_test_suits_count > 0:
            test_suits_result.append(
                log_color_provider.colorize("RED", f"{broken_test_suits_count} broken")
            )
        if failed_test_suits_count > 0:
            test_suits_result.append(
                log_color_provider.colorize("RED", f"{failed_test_suits_count} failed")
            )
        if passed_test_suits_count > 0:
            test_suits_result.append(
                log_color_provider.colorize(
                    "GREEN", f"{passed_test_suits_count} passed"
                )
            )
        if total_test_suits_count > 0:
            test_suits_result.append(f"{total_test_suits_count} total")

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                broken_count=broken_test_suits_count,
                failed_count=failed_test_suits_count,
                passed_count=passed_test_suits_count,
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
