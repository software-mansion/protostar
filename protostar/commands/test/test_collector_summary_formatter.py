from dataclasses import dataclass
from typing import List

from typing_extensions import Self

from .test_collector import TestCollector


class TestCollectorSummaryFormatter:
    @dataclass
    class ViewModel:
        test_case_count: int
        test_suite_count: int
        duration_in_sec: float

        @classmethod
        def from_test_result_summary(
            cls, test_collector_result: TestCollector.Result
        ) -> Self:
            return cls(
                test_case_count=test_collector_result.test_cases_count,
                test_suite_count=len(test_collector_result.test_suites),
                duration_in_sec=test_collector_result.duration,
            )

    def format(self, view_model: ViewModel):
        result: List[str] = ["Collected"]
        result.append(self._format_test_suites_info(view_model.test_suite_count))
        result.append("and")
        result.append(self._format_test_case_info(view_model.test_case_count))
        result.append(f"({view_model.duration_in_sec:.3f} s)")
        return " ".join(result)

    @staticmethod
    def _format_test_suites_info(test_suite_count: int) -> str:
        if test_suite_count == 1:
            return "1 suite,"
        return f"{test_suite_count} suites,"

    @staticmethod
    def _format_test_case_info(test_case_count: int) -> str:
        if test_case_count == 1:
            return "1 test case"
        return f"{test_case_count} test cases"
