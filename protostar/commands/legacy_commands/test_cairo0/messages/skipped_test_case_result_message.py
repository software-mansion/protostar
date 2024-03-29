from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import SkippedTestCaseResult

from .formatters import format_file_path


@dataclass
class SkippedTestCaseResultMessage(StructuredMessage):
    skipped_test_case_result: SkippedTestCaseResult

    def format_human(self, fmt: LogColorProvider) -> str:
        result: list[str] = []
        first_line: list[str] = [f"[{fmt.colorize('YELLOW', 'SKIP')}]"]
        formatted_file_path = format_file_path(
            file_path=self.skipped_test_case_result.file_path, log_color_provider=fmt
        )
        first_line.append(
            f"{formatted_file_path} {self.skipped_test_case_result.test_case_name}"
        )
        result.append(" ".join(first_line))

        reason = self.skipped_test_case_result.reason
        if reason is not None:
            result.append("[reason]:")
            result.append(fmt.colorize("GRAY", reason))
            result.append("")

        return "\n".join(result)

    def format_dict(self) -> dict:
        return {
            "type": "test",
            "message_type": "test_case_result",
            "test_type": "skipped_test_case",
            "test_suite_path": str(self.skipped_test_case_result.file_path),
            "test_case_name": self.skipped_test_case_result.test_case_name,
            "reason": self.skipped_test_case_result.reason,
        }
