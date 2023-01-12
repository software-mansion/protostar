import queue
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from tqdm import tqdm as bar

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.testing.test_scheduler import make_path_relative_if_possible
from protostar.testing import (
    BrokenTestSuiteResult,
    SharedTestsState,
    TestingSummary,
    TestResult,
)
from protostar.io.output import Messenger
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
    ) -> None:
        self._no_progress_bar = no_progress_bar
        self._project_root_path = project_root_path
        self.testing_summary = testing_summary
        self.exit_first = exit_first
        self.slowest_tests_to_report_count = slowest_tests_to_report_count

    def log_json(
        self,
        shared_tests_state: SharedTestsState,
        test_collector_result: "TestCollector.Result",
        messenger: Messenger,
    ):
        try:
            tests_left_n = test_collector_result.test_cases_count
            while tests_left_n > 0:
                test_result: TestResult = shared_tests_state.get_result()

                self.testing_summary.extend([test_result])

                test_result = make_path_relative_if_possible(
                    test_result, self._project_root_path
                )

                messenger(format_test_result(test_result))

                if self.exit_first and shared_tests_state.any_failed_or_broken():
                    tests_left_n = 0
                    return

                if isinstance(test_result, BrokenTestSuiteResult):
                    tests_in_case_count = len(test_result.test_case_names)
                    tests_left_n -= tests_in_case_count
                else:
                    tests_left_n -= 1
        finally:
            messenger(
                TestingSummaryResultMessage(
                    test_collector_result=test_collector_result,
                    testing_summary=self.testing_summary,
                    slowest_tests_to_report_count=self.slowest_tests_to_report_count,
                )
            )

    def log_human(
        self,
        shared_tests_state: SharedTestsState,
        test_collector_result: "TestCollector.Result",
        messenger: Messenger,
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
                        test_result: TestResult = shared_tests_state.get_result()

                        self.testing_summary.extend([test_result])

                        cast(Any, progress_bar).colour = (
                            "RED"
                            if shared_tests_state.any_failed_or_broken()
                            else "GREEN"
                        )

                        test_result = make_path_relative_if_possible(
                            test_result, self._project_root_path
                        )

                        formatted_test_result = format_test_result(test_result)
                        progress_bar.write(
                            formatted_test_result.format_human(fmt=log_color_provider)
                        )

                        if (
                            self.exit_first
                            and shared_tests_state.any_failed_or_broken()
                        ):
                            tests_left_n = 0
                            return

                        if isinstance(test_result, BrokenTestSuiteResult):
                            tests_in_case_count = len(test_result.test_case_names)
                            progress_bar.update(tests_in_case_count)
                            tests_left_n -= tests_in_case_count
                        else:
                            progress_bar.update(1)
                            tests_left_n -= 1
                finally:
                    progress_bar.write("")
                    progress_bar.clear()
                    messenger(
                        TestingSummaryResultMessage(
                            test_collector_result=test_collector_result,
                            testing_summary=self.testing_summary,
                            slowest_tests_to_report_count=self.slowest_tests_to_report_count,
                        )
                    )
        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass
