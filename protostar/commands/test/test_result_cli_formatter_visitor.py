from logging import Logger
from pathlib import Path
from typing import Dict, List

from protostar.commands.test.test_cases import TestResultVisitor
from protostar.commands.test.test_environment_exceptions import ExceptionMetadata
from protostar.commands.test.test_output_recorder import OutputName, format_output_name
from protostar.utils.log_color_provider import LogColorProvider


class TestResultCLIFormatterVisitor(TestResultVisitor):
    def __init__(self, logger: Logger, log_color_provider: LogColorProvider) -> None:
        super().__init__()
        self._logger = logger
        self._log_color_provider = log_color_provider

    def visit_passed_test_case_result(self, passed_test_case_result):
        first_line_elements: List[str] = []
        first_line_elements.append(
            f"[{self._log_color_provider.colorize('GREEN', 'PASS')}]"
        )
        first_line_elements.append(
            f"{self._get_formatted_file_path(passed_test_case_result.file_path)} {passed_test_case_result.test_case_name}"
        )

        info_items: List[str] = []

        info_items.append(
            self._get_formatted_execution_time(passed_test_case_result.execution_time)
        )

        if passed_test_case_result.fuzz_runs_count is not None:
            info_items.append(
                f"fuzz_runs={self._log_color_provider.bold(passed_test_case_result.fuzz_runs_count)}"
            )

        if passed_test_case_result.execution_resources:
            if passed_test_case_result.execution_resources.n_steps:
                info_items.append(
                    f"steps={self._log_color_provider.bold(passed_test_case_result.execution_resources.n_steps)}"
                )
            if passed_test_case_result.execution_resources.n_memory_holes:
                info_items.append(
                    f"memory_holes={self._log_color_provider.bold(passed_test_case_result.execution_resources.n_memory_holes)}"
                )

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_elements.append(
                self._log_color_provider.colorize("GRAY", f"({info})")
            )

        first_line = " ".join(first_line_elements)

        second_line_elements: List[str] = []
        if passed_test_case_result.execution_resources:
            for (
                builtin_name,
                builtin_count,
            ) in (
                passed_test_case_result.execution_resources.builtin_name_to_count_map.items()
            ):
                if builtin_count:
                    second_line_elements.append(
                        self._log_color_provider.colorize(
                            "GRAY",
                            f"{builtin_name}={self._log_color_provider.bold(builtin_count)}",
                        )
                    )

        stdout_elements = self._get_formatted_stdout(
            passed_test_case_result.captured_stdout
        )

        if len(second_line_elements) > 0 or len(stdout_elements) > 0:
            second_line_elements.insert(0, "      ")
            second_line = " ".join(second_line_elements)

            # To maintain consistent spacing
            to_join: List[str] = [first_line, second_line]
            if stdout_elements:
                to_join.append("".join(stdout_elements))
            return "\n".join(to_join)

        return first_line

    def visit_failed_test_case_result(self, failed_test_case_result):
        result: List[str] = []
        first_line_items: List[str] = []

        first_line_items.append(f"[{self._log_color_provider.colorize('RED', 'FAIL')}]")
        first_line_items.append(
            f"{self._get_formatted_file_path(failed_test_case_result.file_path)} {failed_test_case_result.test_case_name}"
        )

        info_items = []

        info_items.append(
            self._get_formatted_execution_time(failed_test_case_result.execution_time)
        )

        for key, value in failed_test_case_result.exception.execution_info.items():
            info_items.append(f"{key}={self._log_color_provider.bold(value)}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_items.append(
                self._log_color_provider.colorize("GRAY", f"({info})")
            )

        result.append(" ".join(first_line_items))

        result.append("\n")
        result.append(str(failed_test_case_result.exception))
        result.append("\n")

        for metadata in failed_test_case_result.exception.metadata:
            result.append(self._get_formatted_metadata(metadata))
            result.append("\n")

        result.extend(
            self._get_formatted_stdout(failed_test_case_result.captured_stdout)
        )

        return "".join(result)

    def visit_passed_fuzz_test_case_result(self):
        pass

    def visit_failed_fuzz_test_case_result(self):
        pass

    def visit_broken_test_suite_result(self):
        pass

    def visit_unexpected_exception_test_suite_result(self):
        pass

    def _get_formatted_file_path(self, file_path: Path) -> str:
        return self._log_color_provider.colorize("GRAY", str(file_path))

    def _get_formatted_execution_time(self, execution_time: float) -> str:
        return f"time={self._log_color_provider.bold(f'{execution_time:.2f}')}s"

    def _get_formatted_stdout(
        self, captured_stdout: Dict[OutputName, str]
    ) -> List[str]:
        result: List[str] = []

        if len(captured_stdout) == 0 or all(
            len(val) == 0 for _, val in captured_stdout.items()
        ):
            return []

        result.append(
            f"\n[{self._log_color_provider.colorize('CYAN', 'captured stdout')}]:\n"
        )

        for name, value in captured_stdout.items():
            if value:
                result.append(
                    f"[{format_output_name(name)}]:\n{self._log_color_provider.colorize('GRAY', value)}\n"
                )

        return result

    def _get_formatted_metadata(self, metadata: ExceptionMetadata) -> str:
        return f"[{metadata.name}]:\n{metadata.format()}"
