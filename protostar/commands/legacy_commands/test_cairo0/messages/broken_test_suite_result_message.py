from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import BrokenTestSuiteResult

from .formatters import format_file_path


@dataclass
class BrokenTestSuiteResultMessage(StructuredMessage):
    broken_test_suite_result: BrokenTestSuiteResult

    def format_human(self, fmt: LogColorProvider) -> str:
        first_line: list[str] = [
            f"[{fmt.colorize('RED', 'BROKEN')}]",
            f"{format_file_path(file_path=self.broken_test_suite_result.file_path, log_color_provider=fmt)}",
        ]
        result = [" ".join(first_line), str(self.broken_test_suite_result.exception)]
        return "\n".join(result)

    def format_dict(self) -> dict:
        return {
            "type": "test",
            "message_type": "test_case_result",
            "test_type": "broken_test_suite",
            "test_suite_path": str(self.broken_test_suite_result.file_path),
            "exception": str(self.broken_test_suite_result.exception),
        }
