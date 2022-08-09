from dataclasses import dataclass

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
        n_test_suites = self._format_test_suites_info(view_model.test_suite_count)
        n_test_cases = self._format_test_case_info(view_model.test_case_count)
        duration = self._format_duration(view_model.duration_in_sec)
        return f"Collected {n_test_suites}, and {n_test_cases} ({duration})"

    @staticmethod
    def _format_test_suites_info(test_suite_count: int) -> str:
        if test_suite_count == 1:
            return "1 suite"
        return f"{test_suite_count} suites"

    @staticmethod
    def _format_test_case_info(test_case_count: int) -> str:
        if test_case_count == 1:
            return "1 test case"
        return f"{test_case_count} test cases"

    @staticmethod
    def _format_duration(duration_in_sec: float) -> str:
        return f"{duration_in_sec:.3f} s"
