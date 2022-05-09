import asyncio
import multiprocessing
import queue
import signal
from logging import Logger
from typing import TYPE_CHECKING, Any, List, cast

from tqdm import tqdm as bar

from src.commands.test.cases import BrokenTest
from src.commands.test.runner import TestRunner
from src.commands.test.test_subject_queue import TestSubject, TestSubjectQueue
from src.commands.test.testing_summary import TestingSummary

if TYPE_CHECKING:
    from src.commands.test.test_collector import TestCollector


class ReporterCoordinator:
    def __init__(
        self,
        logger: Logger,
    ):
        self._logger = logger

    def run(
        self, test_collector_result: "TestCollector.Result", include_paths: List[str]
    ):
        with multiprocessing.Manager() as manager:
            testing_queue = TestSubjectQueue(manager.Queue())
            setups = [
                (
                    subject,
                    testing_queue,
                    include_paths,
                )
                for subject in test_collector_result.test_subjects
            ]

            try:
                with multiprocessing.Pool(
                    multiprocessing.cpu_count(), init_pool
                ) as pool:
                    pool.starmap_async(run_test_subject_worker, setups)
                    self.log_until_finished(testing_queue, test_collector_result)
            except KeyboardInterrupt:
                return

    def log_until_finished(
        self,
        test_subject_queue: TestSubjectQueue,
        test_collector_result: "TestCollector.Result",
    ):
        testing_summary = TestingSummary([])

        try:
            with bar(
                total=test_collector_result.test_cases_count,
                bar_format="{l_bar}{bar}[{n_fmt}/{total_fmt}]",
                dynamic_ncols=True,
            ) as progress_bar:
                tests_left_n = test_collector_result.test_cases_count
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
                        logger=self._logger,
                        collected_test_cases_count=test_collector_result.test_cases_count,
                        collected_test_files_count=len(
                            test_collector_result.test_subjects
                        ),
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
