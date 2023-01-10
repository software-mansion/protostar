from dataclasses import dataclass

from protostar.io import StructuredMessage, LogColorProvider
from protostar.testing import FailedTestCaseResult

from .formatters import (
    format_execution_time_human,
    format_execution_time_structured,
    format_file_path,
    format_stdout,
    format_metadata,
)


@dataclass
class FailedTestCaseResultMessage(StructuredMessage):
    failed_test_case_result: FailedTestCaseResult

    def format_human(self, fmt: LogColorProvider) -> str:

        result: list[str] = []
        first_line_items: list[str] = [f"[{fmt.colorize('RED', 'FAIL')}]"]

        formatted_file_path = format_file_path(
            file_path=self.failed_test_case_result.file_path, log_color_provider=fmt
        )
        first_line_items.append(
            f"{formatted_file_path} {self.failed_test_case_result.test_case_name}"
        )

        info_items = [
            format_execution_time_human(
                execution_time=self.failed_test_case_result.execution_time,
                log_color_provider=fmt,
            )
        ]

        for key, value in self.failed_test_case_result.exception.execution_info.items():
            info_items.append(f"{key}={fmt.bold(value)}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_items.append(fmt.colorize("GRAY", f"({info})"))

        result.append(" ".join(first_line_items))

        result.append("\n")
        result.append(str(self.failed_test_case_result.exception))
        result.append("\n")

        for metadata in self.failed_test_case_result.exception.metadata:
            result.append(format_metadata(metadata))
            result.append("\n")

        result.extend(
            format_stdout(
                captured_stdout=self.failed_test_case_result.captured_stdout,
                log_color_provider=fmt,
            )
        )

        return "".join(result)

    def format_dict(self) -> dict:
        return {
            "message_type": "test_case_result",
            "test_type": "failed_test_case",
            "test_suite_path": str(self.failed_test_case_result.file_path),
            "test_case_name": self.failed_test_case_result.test_case_name,
            "execution_time_in_seconds": format_execution_time_structured(
                self.failed_test_case_result.execution_time
            ),
            "exception": str(self.failed_test_case_result.exception),
            "stdout": str(self.failed_test_case_result.captured_stdout),
        }
