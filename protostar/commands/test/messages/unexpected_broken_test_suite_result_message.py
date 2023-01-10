from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import UnexpectedBrokenTestSuiteResult
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG

from .formatters import format_file_path


@dataclass
class UnexpectedBrokenTestSuiteResultMessage(StructuredMessage):
    unexpected_exception_test_suite_result: UnexpectedBrokenTestSuiteResult

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = []
        main_line: list[str] = [
            f"[{fmt.colorize('RED', 'UNEXPECTED_EXCEPTION')}]",
            format_file_path(
                file_path=self.unexpected_exception_test_suite_result.file_path,
                log_color_provider=fmt,
            ),
        ]
        lines.append(" ".join(main_line))

        if self.unexpected_exception_test_suite_result.traceback:
            lines.append(self.unexpected_exception_test_suite_result.traceback)

        lines.append(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        lines.append(str(self.unexpected_exception_test_suite_result.exception))
        return "\n".join(lines)

    def format_dict(self) -> dict:
        return {
            "message_type": "test_case_result",
            "test_type": "unexpected_broken_test_suite",
            "test_suite_path": str(
                self.unexpected_exception_test_suite_result.file_path
            ),
            "exception": str(self.unexpected_exception_test_suite_result.exception),
            "traceback": self.unexpected_exception_test_suite_result.traceback,
            "protostar_message": UNEXPECTED_PROTOSTAR_ERROR_MSG,
        }
