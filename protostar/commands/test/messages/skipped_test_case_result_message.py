from dataclasses import dataclass

from protostar.io import LogColorProvider
from protostar.testing import SkippedTestCaseResult

from .test_case_result_message import (
    TestCaseResultMessage,
    get_formatted_file_path,
)


@dataclass
class SkippedTestCaseResultMessage(TestCaseResultMessage):
    skipped_test_case_result: SkippedTestCaseResult

    def format_human(self, fmt: LogColorProvider) -> str:
        result: list[str] = []
        first_line: list[str] = [f"[{fmt.colorize('YELLOW', 'SKIP')}]"]
        formatted_file_path = get_formatted_file_path(
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
            "type": "test_case_result",
            "status": "skipped",
            "test_suite_path": str(self.skipped_test_case_result.file_path),
            "test_case_name": self.skipped_test_case_result.test_case_name,
            "reason": self.skipped_test_case_result.reason,
        }
