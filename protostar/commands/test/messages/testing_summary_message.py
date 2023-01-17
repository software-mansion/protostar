from dataclasses import dataclass
import os

from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import TestCollector
from protostar.testing import TestingSummary
from protostar.io.log_color_provider import log_color_provider

from .formatters import format_execution_time_structured


def _format_slow_test_cases_list(
    testing_summary: TestingSummary,
    count: int,
    local_log_color_provider: LogColorProvider = log_color_provider,
) -> str:
    slowest_test_cases = testing_summary.get_slowest_test_cases_list(count)

    rows: list[list[str]] = []
    for i, test_case in enumerate(slowest_test_cases, 1):
        row: list[str] = [
            f"{local_log_color_provider.colorize('CYAN', str(i))}.",
            f"{local_log_color_provider.colorize('GRAY', str(test_case.file_path))}",
            test_case.test_case_name,
            local_log_color_provider.colorize(
                "GRAY",
                f"(time={local_log_color_provider.bold(f'{test_case.execution_time:.2f}')}s)",
            ),
        ]

        rows.append(row)

    column_widths = [max(map(len, col)) for col in zip(*rows)]
    return "\n".join(
        "  ".join((val.ljust(width) for val, width in zip(row, column_widths)))
        for row in rows
    )


def _get_preprocessed_core_testing_summary(
    broken_count: int = 0,
    failed_count: int = 0,
    passed_count: int = 0,
    skipped_count: int = 0,
    total_count: int = 0,
) -> list[str]:
    test_suites_result: list[str] = []

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


@dataclass
class TestingSummaryResultMessage(StructuredMessage):
    test_collector_result: TestCollector.Result
    testing_summary: TestingSummary
    slowest_tests_to_report_count: int

    def format_human(self, fmt: LogColorProvider) -> str:
        result_arr = []
        if (
            self.slowest_tests_to_report_count
            and (len(self.testing_summary.failed) + len(self.testing_summary.passed))
            > 0
        ):
            item = fmt.bold("Slowest test cases:")
            item += _format_slow_test_cases_list(
                testing_summary=self.testing_summary,
                count=self.slowest_tests_to_report_count,
            )
            result_arr.append(item)

        header = fmt.bold("Test suites: ")
        header_size = len(header)

        item = header.ljust(header_size)
        item += self._get_test_suites_summary()
        result_arr.append(item)

        item = fmt.bold("Tests: ").ljust(header_size)
        item += self._get_test_cases_summary()
        result_arr.append(item)

        item = fmt.bold("Seed: ").ljust(header_size)
        item += str(self.testing_summary.testing_seed)
        result_arr.append(item)

        return os.linesep.join(result_arr)

    def format_dict(self) -> dict:
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
        for test_suite in self.test_collector_result.test_suites:
            if str(test_suite.test_path) in failed_tests_paths:
                failed_test_suites += 1
            else:
                passed_test_suites += 1

        return {
            "type": "test",
            "message_type": "testing_summary",
            "test_suite_counts": {
                "total": failed_test_suites + passed_test_suites,
                "failed": failed_test_suites,
                "passed": passed_test_suites,
                "skipped": self.testing_summary.get_skipped_test_suites(),
            },
            "test_case_counts": {
                "total": self.test_collector_result.test_cases_count,
                "broken": len(self.testing_summary.broken),
                "failed": failed_tests,
                "passed": passed_tests,
                "skipped": self.testing_summary.get_skipped_test_cases(),
            },
            "seed": self.testing_summary.testing_seed,
            "execution_time_in_seconds": format_execution_time_structured(
                sum(execution_times)
            ),
        }

    def _get_test_suites_summary(self) -> str:
        passed_test_suites_count = 0
        failed_test_suites_count = 0
        broken_test_suites_count = 0
        total_test_suites_count = len(self.test_collector_result.test_suites)
        for suite_case_results in self.testing_summary.test_suites_mapping.values():
            partial_summary = TestingSummary(
                initial_test_results=suite_case_results,
                testing_seed=self.testing_summary.testing_seed,
                test_collector_result=self.test_collector_result,
            )

            if len(partial_summary.broken_suites) + len(partial_summary.broken) > 0:
                broken_test_suites_count += 1
                continue

            if len(partial_summary.failed) > 0:
                failed_test_suites_count += 1
                continue

            if len(partial_summary.passed) > 0:
                passed_test_suites_count += 1

        test_suites_result: list[str] = []

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
            _get_preprocessed_core_testing_summary(
                broken_count=broken_test_suites_count,
                failed_count=failed_test_suites_count,
                passed_count=passed_test_suites_count,
                skipped_count=self.testing_summary.get_skipped_test_suites(),
                total_count=total_test_suites_count,
            )
        )

    def _get_test_cases_summary(self) -> str:
        return ", ".join(
            _get_preprocessed_core_testing_summary(
                broken_count=len(self.testing_summary.broken),
                failed_count=len(self.testing_summary.failed),
                passed_count=len(self.testing_summary.passed),
                skipped_count=self.testing_summary.get_skipped_test_cases(),
                total_count=self.test_collector_result.test_cases_count,
            )
        )
