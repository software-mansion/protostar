import os
from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import (
    TestCollector,
)

from .formatters import format_execution_time_structured
from .broken_test_suite_result_message import BrokenTestSuiteResultMessage


def _format_test_suites_info(test_suite_count: int) -> str:
    if test_suite_count == 1:
        return "1 suite"
    return f"{test_suite_count} suites"


def _format_test_case_info(test_case_count: int) -> str:
    if test_case_count == 1:
        return "1 test case"
    return f"{test_case_count} test cases"


@dataclass
class TestCollectorResultMessage(StructuredMessage):
    test_collector_result: TestCollector.Result

    def format_human(self, fmt: LogColorProvider) -> str:
        result = []
        for broken_test_suite in self.test_collector_result.broken_test_suites:
            result.append(
                BrokenTestSuiteResultMessage(broken_test_suite).format_human(fmt)
            )
        if self.test_collector_result.test_cases_count:
            n_test_suites = _format_test_suites_info(
                len(self.test_collector_result.test_suites)
            )
            n_test_cases = _format_test_case_info(
                self.test_collector_result.test_cases_count
            )
            duration = format_execution_time_structured(
                self.test_collector_result.duration
            )
            result.append(f"Collected {n_test_suites}, and {n_test_cases} ({duration})")
        elif not result:
            result.append("No test cases found")
        return os.linesep.join(result)

    def format_dict(self) -> dict:
        return {
            "type": "test",
            "message_type": "test_collector_result",
            "broken_test_suites_count": len(
                self.test_collector_result.broken_test_suites
            ),
            "test_suites_count": len(self.test_collector_result.test_suites),
            "test_cases_count": sum(
                len(test_suite.test_cases)
                for test_suite in self.test_collector_result.test_suites
            ),
            "duration_in_seconds": format_execution_time_structured(
                self.test_collector_result.duration
            ),
        }
