from collections import defaultdict
from logging import Logger
from pathlib import Path
from typing import Dict, List, Union

from protostar.commands.test.test_cases import (
    BrokenTestSuite,
    FailedTestCase,
    PassedTestCase,
    TestCaseResult,
)
from protostar.commands.test.testing_seed import TestingSeed
from protostar.protostar_exception import ProtostarExceptionSilent
from protostar.utils.log_color_provider import log_color_provider


class TestingSummary:
    def __init__(
        self, case_results: List[TestCaseResult], testing_seed: TestingSeed
    ) -> None:
        self.testing_seed = testing_seed
        self.case_results = []
        self.test_suites_mapping: Dict[Path, List[TestCaseResult]] = defaultdict(list)
        self.passed: List[PassedTestCase] = []
        self.failed: List[FailedTestCase] = []
        self.broken: List[BrokenTestSuite] = []
        self.extend(case_results)

    def extend(self, case_results: List[TestCaseResult]):
        self.case_results += case_results
        for case_result in case_results:
            self.test_suites_mapping[case_result.file_path].append(case_result)

            if isinstance(case_result, PassedTestCase):
                self.passed.append(case_result)
            if isinstance(case_result, FailedTestCase):
                self.failed.append(case_result)
            if isinstance(case_result, BrokenTestSuite):
                self.broken.append(case_result)

    def log(
        self,
        logger: Logger,
        collected_test_cases_count: int,
        collected_test_suites_count: int,
    ):
        header_width = len("Test suites: ")

        logger.info(
            log_color_provider.bold("Test suites: ".ljust(header_width))
            + self._get_test_suites_summary(collected_test_suites_count)
        )
        logger.info(
            log_color_provider.bold("Tests: ".ljust(header_width))
            + self._get_test_cases_summary(collected_test_cases_count)
        )

        if self.testing_seed.was_used:
            logger.info(
                log_color_provider.bold("Seed: ".ljust(header_width))
                + str(self.testing_seed.value)
            )

    def log_slowest(
        self,
        logger: Logger,
        slowest_tests_to_report_count: int,
    ):
        try:
            if (
                slowest_tests_to_report_count
                and (len(self.failed) + len(self.passed)) > 0
            ):
                logger.info(log_color_provider.bold("Slowest test cases:"))
                print(
                    self._get_formatted_slow_tests(slowest_tests_to_report_count),
                    end="\n\n",
                )
        except KeyboardInterrupt:  # Avoid traceback
            pass

    def assert_all_passed(self):
        if self.failed or self.broken:
            raise ProtostarExceptionSilent("Not all test cases passed")

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

    def _get_test_suites_summary(self, collected_test_suites_count: int) -> str:
        passed_test_suites_count = 0
        failed_test_suites_count = 0
        broken_test_suites_count = 0
        total_test_suites_count = len(self.test_suites_mapping)
        for suit_case_results in self.test_suites_mapping.values():
            partial_summary = TestingSummary(suit_case_results, self.testing_seed)

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
                total_count=collected_test_suites_count,
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

    def _get_slowest_list(
        self,
        failed_and_passed_list: List[Union[PassedTestCase, FailedTestCase]],
        count: int,
    ) -> List[Union[PassedTestCase, FailedTestCase]]:
        lst = sorted(
            failed_and_passed_list, key=lambda x: x.execution_time, reverse=True
        )
        return lst[: min(count, len(lst))]

    def _get_formatted_slow_tests(self, count: int) -> str:

        slowest = self._get_slowest_list(self.failed + self.passed, count)  # type: ignore

        rows: List[List[str]] = []
        for i, test_case in enumerate(slowest, 1):
            row: List[str] = []
            row.append(f"{log_color_provider.colorize('CYAN', str(i))}.")

            row.append(
                f"{log_color_provider.colorize('GRAY', str(test_case.file_path))}"
            )
            row.append(test_case.test_case_name)

            row.append(
                log_color_provider.colorize(
                    "GRAY",
                    f"(time={log_color_provider.bold(f'{test_case.execution_time:.2f}')}s)",
                )
            )

            rows.append(row)

        widths = [max(map(len, col)) for col in zip(*rows)]
        return "\n".join(
            "  ".join((val.ljust(width) for val, width in zip(row, widths)))
            for row in rows
        )
