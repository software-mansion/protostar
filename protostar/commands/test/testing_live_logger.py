import json
import queue
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast, Optional
import math
from tqdm import tqdm as bar

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.testing.test_scheduler import make_path_relative_if_possible
from protostar.testing import (
    BrokenTestSuiteResult,
    SharedTestsState,
    TestingSummary,
    TestResult,
    calculate_skipped,
)
from protostar.starknet.data_transformer import PythonData
from protostar.io.output import Messenger
from protostar.io.log_color_provider import log_color_provider

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

    def get_structured_testing_summary(
        self, test_collector_result: "TestCollector.Result"
    ) -> PythonData:

        failed_tests = len(self.testing_summary.failed)
        passed_tests = len(self.testing_summary.passed)
        execution_times = [
            test.execution_time
            for test in self.testing_summary.passed + self.testing_summary.failed
        ]

        failed_tests_paths = {
            str(item.file_path) for item in self.testing_summary.failed
        }
        passed_test_suites = failed_test_suites = 0
        for test_suite in test_collector_result.test_suites:
            if str(test_suite.test_path) in failed_tests_paths:
                failed_test_suites += 1
            else:
                passed_test_suites += 1

        return {
            "type": "test_summary",
            "test_suite_counts": {
                "total": failed_test_suites + passed_test_suites,
                "failed": failed_test_suites,
                "passed": passed_test_suites,
                "skipped": calculate_skipped(
                    total_count=len(test_collector_result.test_suites),
                    broken_count=len(self.testing_summary.broken_suites),
                    failed_count=failed_test_suites,
                    passed_count=passed_test_suites,
                ),
            },
            "test_case_counts": {
                "total": test_collector_result.test_cases_count,
                "failed": failed_tests,
                "passed": passed_tests,
                "skipped": calculate_skipped(
                    total_count=test_collector_result.test_cases_count,
                    broken_count=len(self.testing_summary.broken),
                    failed_count=failed_tests,
                    passed_count=passed_tests,
                ),
            },
            "seed": self.testing_summary.testing_seed,
            "execution_time_in_seconds": math.floor(sum(execution_times) * 100) / 100,
        }

    def log_testing_summary(
        self, test_collector_result: "TestCollector.Result"
    ) -> None:
        self.testing_summary.log(
            collected_test_cases_count=test_collector_result.test_cases_count,
            collected_test_suites_count=len(test_collector_result.test_suites),
            slowest_test_cases_to_report_count=self.slowest_tests_to_report_count,
        )

    def log(
        self,
        shared_tests_state: SharedTestsState,
        test_collector_result: "TestCollector.Result",
        structured_format: bool,
        messanger: Optional[Messenger] = None,
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
                        if structured_format:
                            assert messanger is not None
                            messanger(formatted_test_result)  # ???
                        else:
                            progress_bar.write(
                                formatted_test_result.format_human(
                                    fmt=log_color_provider
                                )
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
                    if structured_format:
                        print(
                            json.dumps(
                                self.get_structured_testing_summary(
                                    test_collector_result
                                )
                            )
                        )
                    else:
                        progress_bar.write("")
                        progress_bar.clear()
                        self.log_testing_summary(test_collector_result)

        except queue.Empty:
            # https://docs.python.org/3/library/queue.html#queue.Queue.get
            # We skip it to prevent deadlock, but this error should never happen
            pass
