from typing import Any

from protostar.commands.test.test_result_formatter import format_test_result
from protostar.io.log_color_provider import LogColorProvider
from protostar.testing import TestCaseResult, TestingSummary
from tests._conftest.cairo_test_results.cairo_test_results_data import (
    CairoTestResultsData,
)


class CairoTestCasesDiff:
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
        expected: CairoTestResultsData,
        actual: CairoTestResultsData,
    ) -> str:
        lines: list[str] = []
        for expected_result_type in ["passed", "failed", "broken", "skipped"]:
            for expected_test_case_name in getattr(expected, expected_result_type):
                if expected_test_case_name in getattr(actual, expected_result_type):
                    continue
                lines.append(
                    (
                        f"Expected '{expected_test_case_name}' to be {expected_result_type}, got:"
                    )
                )
                lines.append(
                    format_test_result(
                        self._get_test_case_result(expected_test_case_name)
                    ).format_human(LogColorProvider())
                )
                lines.append("")
                break
        return "\n".join(lines)

    def _fn(self):
        if expected_test_case_name in getattr(actual, expected_result_type):
            continue
        lines.append(
            (f"Expected '{expected_test_case_name}' to be {expected_result_type}, got:")
        )
        lines.append(
            format_test_result(
                self._get_test_case_result(expected_test_case_name)
            ).format_human(LogColorProvider())
        )
        lines.append("")
        break

    def _get_test_case_result(self, test_case_name: str) -> TestCaseResult:
        assert (
            test_case_name in self._test_case_name_to_result
        ), "Test suite could be broken"
        return self._test_case_name_to_result[test_case_name]
