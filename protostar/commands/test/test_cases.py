from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG
from protostar.utils.log_color_provider import log_color_provider


@dataclass(frozen=True)
class TestCaseResult:
    file_path: Path

    def get_formatted_file_path(self):
        return log_color_provider.colorize("GRAY", str(self.file_path))

    @abstractmethod
    def log(self, _: bool = False) -> str:
        ...


@dataclass(frozen=True)
class PassedTestCase(TestCaseResult):
    test_case_name: str
    execution_resources: Optional[ExecutionResourcesSummary]
    captured_setup_stdout: str
    captured_test_stdout: str

    def log(self, include_stdout_section: bool = False) -> str:
        first_line_elements: List[str] = []
        first_line_elements.append(f"[{log_color_provider.colorize('GREEN', 'PASS')}]")
        first_line_elements.append(
            f"{self.get_formatted_file_path()} {self.test_case_name}"
        )

        if self.execution_resources:
            common_execution_resources_elements: List[str] = []
            common_execution_resources_elements.append(
                f"steps={log_color_provider.bold(self.execution_resources.n_steps)}"
            )
            if self.execution_resources.n_memory_holes:
                common_execution_resources_elements.append(
                    f"memory_holes={log_color_provider.bold(self.execution_resources.n_memory_holes)}"
                )
            merged_common_execution_resource_info = ", ".join(
                common_execution_resources_elements
            )
            first_line_elements.append(
                log_color_provider.colorize(
                    "GRAY", f"({merged_common_execution_resource_info})"
                )
            )

        first_line = " ".join(first_line_elements)

        second_line_elements: List[str] = []
        if self.execution_resources:
            for (
                builtin_name,
                builtin_count,
            ) in self.execution_resources.builtin_name_to_count_map.items():
                if builtin_count > 0:
                    second_line_elements.append(
                        log_color_provider.colorize(
                            "GRAY",
                            f"{builtin_name}={log_color_provider.bold(builtin_count)}",
                        )
                    )

        stdout_elements: List[str] = []
        if (
            self.captured_test_stdout or self.captured_setup_stdout
        ) and include_stdout_section:
            stdout_elements.append(
                f"[{log_color_provider.colorize('GREEN', 'captured stdout')}]:"
            )

            if self.captured_setup_stdout:
                stdout_elements.append(
                    "[setup]:\n"
                    f"{log_color_provider.colorize('GRAY', self.captured_setup_stdout)}"
                )

            if self.captured_test_stdout:
                stdout_elements.append(
                    "[test]:\n"
                    f"{log_color_provider.colorize('GRAY', self.captured_test_stdout)}"
                )

        if len(second_line_elements) > 0 or len(stdout_elements) > 0:
            second_line_elements.insert(0, "      ")
            second_line = " ".join(second_line_elements)
            stdout_lines = "\n".join(stdout_elements)
            return "\n".join([first_line, second_line, stdout_lines])

        return first_line


@dataclass(frozen=True)
class FailedTestCase(TestCaseResult):
    test_case_name: str
    exception: ReportedException
    captured_setup_stdout: str
    captured_test_stdout: str

    def log(self, include_stdout_section: bool = True) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('RED', 'FAIL')}] ")
        result.append(f"{self.get_formatted_file_path()} {self.test_case_name}")
        result.append("\n")
        result.append(str(self.exception))
        result.append("\n")

        if (
            self.captured_test_stdout or self.captured_setup_stdout
        ) and include_stdout_section:
            result.append(
                f"\n[{log_color_provider.colorize('RED', 'captured stdout')}]:\n"
            )

            if self.captured_setup_stdout:
                result.append(
                    "[setup]:\n"
                    f"{log_color_provider.colorize('GRAY', self.captured_setup_stdout)}\n"
                )

            if self.captured_test_stdout:
                result.append(
                    "[test]:\n"
                    f"{log_color_provider.colorize('GRAY', self.captured_test_stdout)}\n"
                )

        return "".join(result)


@dataclass(frozen=True)
class BrokenTestSuite(TestCaseResult):
    test_case_names: List[str]
    exception: BaseException

    def log(self, _: bool = False) -> str:
        first_line: List[str] = []
        first_line.append(f"[{log_color_provider.colorize('RED', 'BROKEN')}]")
        first_line.append(f"{self.get_formatted_file_path()}")
        result = [" ".join(first_line)]
        result.append(str(self.exception))
        return "\n".join(result)


@dataclass(frozen=True)
class UnexpectedExceptionTestSuiteResult(BrokenTestSuite):
    traceback: Optional[str] = None

    def log(self, _: bool = False) -> str:
        lines: List[str] = []
        main_line: List[str] = []
        main_line.append(
            f"[{log_color_provider.colorize('RED', 'UNEXPECTED_EXCEPTION')}]"
        )
        main_line.append(self.get_formatted_file_path())
        lines.append(" ".join(main_line))

        if self.traceback:
            lines.append(self.traceback)

        lines.append(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        lines.append(str(self.exception))
        return "\n".join(lines)
