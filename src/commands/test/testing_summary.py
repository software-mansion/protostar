from collections import defaultdict
from logging import Logger
from pathlib import Path
from typing import Dict, List

from src.commands.test.test_cases import (
    BrokenTestFile,
    FailedTestCase,
    PassedTestCase,
    TestCaseResult,
)
from src.utils.log_color_provider import log_color_provider


class TestingSummary:
    def __init__(self, case_results: List[TestCaseResult]) -> None:
        self.case_results = []
        self.test_files: Dict[Path, List[TestCaseResult]] = defaultdict(list)
        self.passed: List[PassedTestCase] = []
        self.failed: List[FailedTestCase] = []
        self.broken: List[BrokenTestFile] = []
        self.extend(case_results)

    def extend(self, case_results: List[TestCaseResult]):
        self.case_results += case_results
        for case_result in case_results:
            self.test_files[case_result.file_path].append(case_result)

            if isinstance(case_result, PassedTestCase):
                self.passed.append(case_result)
            if isinstance(case_result, FailedTestCase):
                self.failed.append(case_result)
            if isinstance(case_result, BrokenTestFile):
                self.broken.append(case_result)

    def log(
        self,
        logger: Logger,
        collected_test_cases_count: int,
        collected_test_files_count: int,
    ):
        logger.info(
            log_color_provider.bold("Test suites: ")
            + self._get_test_suites_summary(collected_test_files_count)
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

    def _get_test_suites_summary(self, collected_test_files_count: int) -> str:
        passed_test_suites_count = 0
        failed_test_suites_count = 0
        broken_test_suites_count = 0
        total_test_suites_count = len(self.test_files)
        for suit_case_results in self.test_files.values():
            partial_summary = TestingSummary(suit_case_results)

            if len(partial_summary.broken) > 0:
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
