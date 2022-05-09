import asyncio
import multiprocessing
import queue
import signal
from collections import defaultdict
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, cast

from tqdm import tqdm as bar

from src.commands.test.cases import BrokenTest, CaseResult, FailedCase, PassedCase
from src.commands.test.runner import TestRunner
from src.commands.test.test_subject_queue import TestSubject, TestSubjectQueue
from src.utils.log_color_provider import log_color_provider


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

    def log(
        self,
        logger: Logger,
        collected_test_cases_count: int,
        collected_test_files_count: int,
    ):
        logger.info(
            log_color_provider.bold("Test suits: ")
            + self._get_test_suits_summary(collected_test_files_count)
        )
        logger.info(
            log_color_provider.bold("Tests:      ")
            + self._get_test_cases_summary(collected_test_cases_count)
        )

    def _get_test_cases_summary(self, collected_test_cases_count: int) -> str:
        failed_test_cases_count = len(self.failed)
        passed_test_cases_count = len(self.passed)

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                failed_count=failed_test_cases_count,
                passed_count=passed_test_cases_count,
                total_count=collected_test_cases_count,
            )
        )

    def _get_test_suits_summary(self, collected_test_files_count: int) -> str:
        passed_test_suits_count = 0
        failed_test_suits_count = 0
        broken_test_suits_count = 0
        total_test_suits_count = len(self.test_files)
        for suit_case_results in self.test_files.values():
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
                total_count=collected_test_files_count,
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


class ReporterCoordinator:
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

    def run(self, test_subjects: List[TestSubject], include_paths: List[str]):
        with multiprocessing.Manager() as manager:
            testing_queue = TestSubjectQueue(manager.Queue())
            setups = [
                (
                    subject,
                    testing_queue,
                    include_paths,
                )
                for subject in test_subjects
            ]

            try:
                with multiprocessing.Pool(
                    multiprocessing.cpu_count(), init_pool
                ) as pool:
                    pool.starmap_async(run_test_subject_worker, setups)
                    self.live_reporting(testing_queue)
            except KeyboardInterrupt:
                return

    def live_reporting(
        self,
        test_subject_queue: TestSubjectQueue,
    ):
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
                        (subject, case_result) = test_subject_queue.dequeue()
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
                    testing_summary.log(
                        logger=self.logger,
                        collected_test_cases_count=self.collected_tests_count,
                        collected_test_files_count=len(self.collected_subjects),
                    )

        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass


def init_pool():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def run_test_subject_worker(
    subject: TestSubject,
    test_subject_queue: TestSubjectQueue,
    include_paths: List[str],
):
    runner = TestRunner(queue=test_subject_queue, include_paths=include_paths)
    asyncio.run(runner.run_test_subject(subject))
    return runner.queue
