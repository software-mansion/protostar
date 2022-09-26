from collections import defaultdict
from logging import Logger
from pathlib import Path
from typing import Dict, List

from protostar.protostar_exception import ProtostarExceptionSilent
from protostar.utils.log_color_provider import LogColorProvider, log_color_provider

from .test_results import (
    BrokenTestCaseResult,
    BrokenTestSuiteResult,
    FailedTestCaseResult,
    PassedTestCaseResult,
    SkippedTestCaseResult,
    TestCaseResult,
    TestResult,
    TimedTestCaseResult,
)
from .testing_seed import Seed


# pylint: disable=too-many-instance-attributes
class TestingSummary:
    def __init__(self, test_results: List[TestResult], testing_seed: Seed) -> None:
        self.testing_seed = testing_seed
        self.test_results: List[TestResult] = []
        self.test_suites_mapping: Dict[Path, List[TestResult]] = defaultdict(list)
        self.passed: List[PassedTestCaseResult] = []
        self.failed: List[FailedTestCaseResult] = []
        self.broken: List[BrokenTestCaseResult] = []
        self.broken_suites: List[BrokenTestSuiteResult] = []
        self.skipped: List[SkippedTestCaseResult] = []
        self.extend(test_results)

    def extend(self, test_results: List[TestResult]):
        self.test_results += test_results
        for case_result in test_results:
            self.test_suites_mapping[case_result.file_path].append(case_result)

            if isinstance(case_result, PassedTestCaseResult):
                self.passed.append(case_result)
            if isinstance(case_result, FailedTestCaseResult):
                self.failed.append(case_result)
            if isinstance(case_result, BrokenTestCaseResult):
                self.broken.append(case_result)
            if isinstance(case_result, BrokenTestSuiteResult):
                self.broken_suites.append(case_result)
            if isinstance(case_result, SkippedTestCaseResult):
                self.skipped.append(case_result)

    def log(
        self,
        logger: Logger,
        collected_test_cases_count: int,
        collected_test_suites_count: int,
        slowest_test_cases_to_report_count: int,
    ):
        self.log_slowest_test_cases(logger, slowest_test_cases_to_report_count)

        header_width = len("Test suites: ")

        logger.info(
            log_color_provider.bold("Test suites: ".ljust(header_width))
            + self._get_test_suites_summary(collected_test_suites_count)
        )
        logger.info(
            log_color_provider.bold("Tests: ".ljust(header_width))
            + self._get_test_cases_summary(collected_test_cases_count)
        )
        logger.info(
            log_color_provider.bold("Seed: ".ljust(header_width))
            + str(self.testing_seed)
        )

    def log_slowest_test_cases(
        self,
        logger: Logger,
        slowest_tests_to_report_count: int,
    ):
        if slowest_tests_to_report_count and (len(self.failed) + len(self.passed)) > 0:
            logger.info(log_color_provider.bold("Slowest test cases:"))
            print(
                self._format_slow_test_cases_list(slowest_tests_to_report_count),
                end="\n\n",
            )

    def assert_all_passed(self):
        if self.failed or self.broken_suites or self.broken:
            raise ProtostarExceptionSilent("Not all test cases passed")

    def _get_test_cases_summary(self, collected_test_cases_count: int) -> str:
        broken_test_cases_count = len(self.broken)
        failed_test_cases_count = len(self.failed)
        passed_test_cases_count = len(self.passed)

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                broken_count=broken_test_cases_count,
                failed_count=failed_test_cases_count,
                passed_count=passed_test_cases_count,
                total_count=collected_test_cases_count,
            )
        )

    def _get_test_suites_summary(self, collected_test_suites_count: int) -> str:
        passed_test_suites_count = 0
        failed_test_suites_count = 0
        broken_test_suites_count = 0
        total_test_suites_count = len(self.test_suites_mapping)
        for suit_case_results in self.test_suites_mapping.values():
            partial_summary = TestingSummary(suit_case_results, self.testing_seed)

            if len(partial_summary.broken_suites) + len(partial_summary.broken) > 0:
                broken_test_suites_count += 1
                continue

            if len(partial_summary.failed) > 0:
                failed_test_suites_count += 1
                continue

            if len(partial_summary.passed) > 0:
                passed_test_suites_count += 1

        test_suites_result: List[str] = []

        if broken_test_suites_count > 0:
            test_suites_result.append(
                log_color_provider.colorize("RED", f"{broken_test_suites_count} broken")
            )
        if failed_test_suites_count > 0:
            test_suites_result.append(
                log_color_provider.colorize("RED", f"{failed_test_suites_count} failed")
            )
        if passed_test_suites_count > 0:
            test_suites_result.append(
                log_color_provider.colorize(
                    "GREEN", f"{passed_test_suites_count} passed"
                )
            )
        if total_test_suites_count > 0:
            test_suites_result.append(f"{total_test_suites_count} total")

        return ", ".join(
            self._get_preprocessed_core_testing_summary(
                broken_count=broken_test_suites_count,
                failed_count=failed_test_suites_count,
                passed_count=passed_test_suites_count,
                total_count=collected_test_suites_count,
            )
        )

    def _get_preprocessed_core_testing_summary(
        self,
        broken_count: int = 0,
        failed_count: int = 0,
        passed_count: int = 0,
        total_count: int = 0,
    ) -> List[str]:
        skipped_count = total_count - (broken_count + failed_count + passed_count)
        test_suites_result: List[str] = []

        if broken_count > 0:
            test_suites_result.append(
                log_color_provider.colorize("RED", f"{broken_count} broken")
            )
        if failed_count > 0:
            test_suites_result.append(
                log_color_provider.colorize("RED", f"{failed_count} failed")
            )
        if skipped_count > 0:
            test_suites_result.append(
                log_color_provider.colorize("YELLOW", f"{skipped_count} skipped")
            )
        if passed_count > 0:
            test_suites_result.append(
                log_color_provider.colorize("GREEN", f"{passed_count} passed")
            )
        if total_count > 0:
            test_suites_result.append(f"{total_count} total")

        return test_suites_result

    def _get_slowest_test_cases_list(
        self,
        count: int,
    ) -> List[TimedTestCaseResult]:
        lst: List[TimedTestCaseResult]
        lst = self.passed + self.failed + self.broken  # type: ignore
        lst.sort(key=lambda x: x.execution_time, reverse=True)
        return lst[: min(count, len(lst))]

    def _format_slow_test_cases_list(
        self,
        count: int,
        local_log_color_provider: LogColorProvider = log_color_provider,
    ) -> str:

        slowest_test_cases = self._get_slowest_test_cases_list(count)

        rows: List[List[str]] = []
        for i, test_case in enumerate(slowest_test_cases, 1):
            row: List[str] = []
            row.append(f"{local_log_color_provider.colorize('CYAN', str(i))}.")

            row.append(
                f"{local_log_color_provider.colorize('GRAY', str(test_case.file_path))}"
            )
            row.append(test_case.test_case_name)

            row.append(
                local_log_color_provider.colorize(
                    "GRAY",
                    f"(time={local_log_color_provider.bold(f'{test_case.execution_time:.2f}')}s)",
                )
            )

            rows.append(row)

        column_widths = [max(map(len, col)) for col in zip(*rows)]
        return "\n".join(
            "  ".join((val.ljust(width) for val, width in zip(row, column_widths)))
            for row in rows
        )

    def __getitem__(self, protostar_test_case_name: str):
        for test_result in self.test_results:
            if (
                isinstance(test_result, TestCaseResult)
                and test_result.test_case_name == protostar_test_case_name
            ):
                return test_result
        assert False, f"Couldn't find '{protostar_test_case_name}' test case result."
