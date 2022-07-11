import queue
from logging import Logger
from typing import TYPE_CHECKING, Any, cast

from tqdm import tqdm as bar

from protostar.commands.test.test_cases import BrokenTestSuite, TestCaseResult
from protostar.commands.test.test_results_queue import TestResultsQueue
from protostar.commands.test.testing_summary import TestingSummary

if TYPE_CHECKING:
    from protostar.commands.test.test_collector import TestCollector


class TestingLiveLogger:
    def __init__(
        self, logger: Logger, testing_summary: TestingSummary, no_progress_bar: bool, exit_first: bool
    ) -> None:
        self._logger = logger
        self._no_progress_bar = no_progress_bar
        self.testing_summary = testing_summary
        self.exit_first = exit_first

    def log(
        self,
        test_results_queue: TestResultsQueue,
        test_collector_result: "TestCollector.Result",
    ):

        try:
            with bar(
                total=test_collector_result.test_cases_count,
                bar_format="{l_bar}{bar}[{n_fmt}/{total_fmt}]",
                dynamic_ncols=True,
                leave=False,
                disable=self._no_progress_bar,
            ) as progress_bar:
                tests_left_n = test_collector_result.test_cases_count
                progress_bar.update()
                try:
                    while tests_left_n > 0:
                        test_case_result: TestCaseResult = test_results_queue.get()

                        self.testing_summary.extend([test_case_result])

                        cast(Any, progress_bar).colour = (
                            "RED" if test_results_queue.failed() else "GREEN"
                        )

                        progress_bar.write(str(test_case_result))
                        if self.exit_first and test_results_queue.failed():
                            tests_left_n = 0
                            return

                        if isinstance(test_case_result, BrokenTestSuite):
                            tests_in_case_count = len(test_case_result.test_case_names)
                            progress_bar.update(tests_in_case_count)
                            tests_left_n -= tests_in_case_count
                        else:
                            progress_bar.update(1)
                            tests_left_n -= 1
                finally:
                    progress_bar.write("")
                    progress_bar.clear()
                    self.testing_summary.log(
                        logger=self._logger,
                        collected_test_cases_count=test_collector_result.test_cases_count,
                        collected_test_suites_count=len(
                            test_collector_result.test_suites
                        ),
                    )

        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass
