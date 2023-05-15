from typing import Any

from protostar.commands.legacy_commands.test_cairo0.test_result_formatter import (
    format_test_result,
)
from protostar.io.log_color_provider import LogColorProvider
from protostar.testing import TestCaseResult, TestingSummary

from .cairo_test_results_data import CairoTestResultsData


class CairoTestCasesDiffGenerator:
    @classmethod
    def from_testing_summary(cls, testing_summary: TestingSummary):
        return cls(
            test_case_name_to_result={
                test_result.test_case_name: test_result
                for test_result in testing_summary.test_results
                if isinstance(test_result, TestCaseResult)
            }
        )

    def __init__(self, test_case_name_to_result: dict[str, Any]) -> None:
        self._test_case_name_to_result = test_case_name_to_result

    def execute(
        self,
        expected_test_results_data: CairoTestResultsData,
        actual_test_results_data: CairoTestResultsData,
    ) -> str:
        lines: list[str] = []
        for expected_result_type in ["passed", "failed", "broken", "skipped"]:
            for expected_test_case_name in getattr(
                expected_test_results_data, expected_result_type
            ):
                if expected_test_case_name in getattr(
                    actual_test_results_data, expected_result_type
                ):
                    continue
                lines.extend(
                    self._create_error_message(
                        expected_test_case_name, expected_result_type
                    )
                )
                lines.append("")
        return "\n".join(lines)

    def _create_error_message(
        self, expected_test_case_name: str, expected_result_type: str
    ):
        lines: list[str] = []
        lines.append(
            (f"Expected '{expected_test_case_name}' to be {expected_result_type}, got:")
        )
        lines.append(
            format_test_result(
                self._get_test_case_result(expected_test_case_name)
            ).format_human(LogColorProvider())
        )
        return lines

    def _get_test_case_result(self, test_case_name: str) -> TestCaseResult:
        assert (
            test_case_name in self._test_case_name_to_result
        ), f"Couldn't find test case result for '{test_case_name}'. Test suite could be broken"
        return self._test_case_name_to_result[test_case_name]
