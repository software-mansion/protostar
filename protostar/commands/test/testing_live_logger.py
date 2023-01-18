import queue
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast, Optional

from tqdm import tqdm as bar

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.testing.test_scheduler import make_path_relative_if_possible
from protostar.testing import (
    AcceptableResult,
    BrokenTestSuiteResult,
    SharedTestsState,
    TestingSummary,
    TestResult,
)
from protostar.io.output import Messenger, HumanMessenger
from protostar.io.log_color_provider import log_color_provider

from .messages import TestingSummaryResultMessage

if TYPE_CHECKING:
    from protostar.testing import TestCollector


class TestingLiveLogger:
    def __init__(
        self,
        testing_summary: TestingSummary,
        no_progress_bar: bool,
        exit_first: bool,
        slowest_tests_to_report_count: int,
        project_root_path: Path,
        write: Messenger,
    ) -> None:
        self._write = write
        self._no_progress_bar = no_progress_bar
        self._project_root_path = project_root_path
        self.testing_summary = testing_summary
        self.exit_first = exit_first
        self.slowest_tests_to_report_count = slowest_tests_to_report_count

    def log(
        self,
        shared_tests_state: SharedTestsState,
        test_collector_result: "TestCollector.Result",
    ) -> None:
        if isinstance(self._write, HumanMessenger):
            try:
                with bar(
                    total=test_collector_result.test_cases_count,
                    bar_format="{l_bar}{bar}[{n_fmt}/{total_fmt}]",
                    dynamic_ncols=True,
                    leave=False,
                    disable=self._no_progress_bar,
                ) as progress_bar:
                    self._log(
                        shared_tests_state=shared_tests_state,
                        test_collector_result=test_collector_result,
                        progress_bar=progress_bar,
                    )
            except queue.Empty:
                # https://docs.python.org/3/library/queue.html#queue.Queue.get
                # We skip it to prevent deadlock, but this error should never happen
                pass
        else:
            self._log(
                shared_tests_state=shared_tests_state,
                test_collector_result=test_collector_result,
            )

    # pylint: disable=too-many-branches
    def _log(
        self,
        shared_tests_state: SharedTestsState,
        test_collector_result: "TestCollector.Result",
        progress_bar: Optional[bar] = None,
    ):
        tests_left_n = test_collector_result.test_cases_count
        if progress_bar:
            progress_bar.update()
        try:
            while tests_left_n > 0:
                test_result: TestResult = shared_tests_state.get_result()

                self.testing_summary.extend([test_result])

                if progress_bar:
                    cast(Any, progress_bar).colour = (
                        "RED" if shared_tests_state.any_failed_or_broken() else "GREEN"
                    )

                test_result = make_path_relative_if_possible(
                    test_result, self._project_root_path
                )

                if progress_bar:
                    formatted_test_result = format_test_result(test_result)
                    progress_bar.write(
                        formatted_test_result.format_human(fmt=log_color_provider)
                    )

                    if self.should_exit(test_result):
                        break
                else:
                    self._write(format_test_result(test_result))

                if isinstance(test_result, BrokenTestSuiteResult):
                    tests_in_case_count = len(test_result.test_case_names)
                    if progress_bar:
                        progress_bar.update(tests_in_case_count)
                    tests_left_n -= tests_in_case_count
                else:
                    if progress_bar:
                        progress_bar.update(1)
                    tests_left_n -= 1
        finally:
            if progress_bar:
                progress_bar.close()
            self._write(
                TestingSummaryResultMessage(
                    test_collector_result=test_collector_result,
                    testing_summary=self.testing_summary,
                    slowest_tests_to_report_count=self.slowest_tests_to_report_count,
                )
            )

    def should_exit(self, test_result: TestResult):
        """
        Check whether we have encountered the first failed, broken or unexpected error test case on the queue.
        """
        return self.exit_first and not isinstance(test_result, AcceptableResult)
