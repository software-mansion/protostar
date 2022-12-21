from dataclasses import dataclass

from protostar.io import LogColorProvider
from protostar.testing import BrokenTestCaseResult

from .test_case_result_message import (
    TestCaseResultMessage,
    get_formatted_execution_time_human,
    get_formatted_execution_time_structured,
    get_formatted_file_path,
    get_formatted_stdout,
    get_formatted_metadata,
)


@dataclass
class BrokenTestCaseResultMessage(TestCaseResultMessage):
    broken_test_case_result: BrokenTestCaseResult

    def format_human(self, fmt: LogColorProvider) -> str:
        result: list[str] = []
        first_line_items: list[str] = [f"[{fmt.colorize('RED', 'BROKEN')}]"]

        formatted_file_path = get_formatted_file_path(
            file_path=self.broken_test_case_result.file_path, log_color_provider=fmt
        )
        first_line_items.append(
            f"{formatted_file_path} {self.broken_test_case_result.test_case_name}"
        )

        info_items = [
            get_formatted_execution_time_human(
                execution_time=self.broken_test_case_result.execution_time,
                log_color_provider=fmt,
            )
        ]

        for key, value in self.broken_test_case_result.exception.execution_info.items():
            info_items.append(f"{key}={fmt.bold(value)}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_items.append(fmt.colorize("GRAY", f"({info})"))

        result.append(" ".join(first_line_items))

        result.append("\n")
        result.append(str(self.broken_test_case_result.exception))
        result.append("\n")

        for metadata in self.broken_test_case_result.exception.metadata:
            result.append(get_formatted_metadata(metadata))
            result.append("\n")

        result.extend(
            get_formatted_stdout(
                captured_stdout=self.broken_test_case_result.captured_stdout,
                log_color_provider=fmt,
            )
        )

        return "".join(result)

    def format_dict(self) -> dict:
        return {
            "type": "test_case_result",
            "status": "broken",
            "test_suite_path": str(self.broken_test_case_result.file_path),
            "test_case_name": self.broken_test_case_result.test_case_name,
            "execution_time_in_seconds": get_formatted_execution_time_structured(
                self.broken_test_case_result.execution_time
            ),
            "exception": self.broken_test_case_result.exception,
            "stdout": str(self.broken_test_case_result.captured_stdout),
        }
