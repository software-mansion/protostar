from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.test_environment_exceptions import (
    ExceptionMetadata,
    ReportedException,
)
from protostar.commands.test.test_output_recorder import OutputName, format_output_name
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG
from protostar.utils.log_color_provider import log_color_provider


@dataclass(frozen=True)
class TestResult:
    file_path: Path

    @abstractmethod
    def format(self) -> str:
        ...


# pylint: disable=abstract-method
@dataclass(frozen=True)
class TestCaseResult(TestResult):
    test_case_name: str
    captured_stdout: Dict[OutputName, str]


@dataclass(frozen=True)
class PassedTestCase(TestCaseResult):
    execution_resources: Optional[ExecutionResourcesSummary]
    execution_time: float
    fuzz_runs_count: Optional[int] = None

    def format(self) -> str:
        first_line_elements: List[str] = []
        first_line_elements.append(f"[{log_color_provider.colorize('GREEN', 'PASS')}]")
        first_line_elements.append(
            f"{_get_formatted_file_path(self.file_path)} {self.test_case_name}"
        )

        info_items: List[str] = []

        info_items.append(_get_formatted_execution_time(self.execution_time))

        if self.fuzz_runs_count is not None:
            info_items.append(
                f"fuzz_runs={log_color_provider.bold(self.fuzz_runs_count)}"
            )

        if self.execution_resources:
            if self.execution_resources.n_steps:
                info_items.append(
                    f"steps={log_color_provider.bold(self.execution_resources.n_steps)}"
                )
            if self.execution_resources.n_memory_holes:
                info_items.append(
                    f"memory_holes={log_color_provider.bold(self.execution_resources.n_memory_holes)}"
                )

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_elements.append(log_color_provider.colorize("GRAY", f"({info})"))

        first_line = " ".join(first_line_elements)

        second_line_elements: List[str] = []
        if self.execution_resources:
            for (
                builtin_name,
                builtin_count,
            ) in self.execution_resources.builtin_name_to_count_map.items():
                if builtin_count:
                    second_line_elements.append(
                        log_color_provider.colorize(
                            "GRAY",
                            f"{builtin_name}={log_color_provider.bold(builtin_count)}",
                        )
                    )

        stdout_elements = _get_formatted_stdout(self.captured_stdout)

        if len(second_line_elements) > 0 or len(stdout_elements) > 0:
            second_line_elements.insert(0, "      ")
            second_line = " ".join(second_line_elements)

            # To maintain consistent spacing
            to_join: List[str] = [first_line, second_line]
            if stdout_elements:
                to_join.append("".join(stdout_elements))
            return "\n".join(to_join)

        return first_line


@dataclass(frozen=True)
class FailedTestCase(TestCaseResult):
    exception: ReportedException
    execution_time: float

    def format(self) -> str:
        result: List[str] = []
        first_line_items: List[str] = []

        first_line_items.append(f"[{log_color_provider.colorize('RED', 'FAIL')}]")
        first_line_items.append(
            f"{_get_formatted_file_path(self.file_path)} {self.test_case_name}"
        )

        info_items = []

        info_items.append(_get_formatted_execution_time(self.execution_time))

        for key, value in self.exception.execution_info.items():
            info_items.append(f"{key}={log_color_provider.bold(value)}")

        if len(info_items) > 0:
            info = ", ".join(info_items)
            first_line_items.append(log_color_provider.colorize("GRAY", f"({info})"))

        result.append(" ".join(first_line_items))

        result.append("\n")
        result.append(str(self.exception))
        result.append("\n")

        for metadata in self.exception.metadata:
            result.append(_get_formatted_metadata(metadata))
            result.append("\n")

        result.extend(_get_formatted_stdout(self.captured_stdout))

        return "".join(result)


@dataclass(frozen=True)
class FuzzResult:
    fuzz_runs_count: Optional[int]


@dataclass(frozen=True)
class PassedFuzzTestCase(PassedTestCase, FuzzResult):
    pass


@dataclass(frozen=True)
class FailedFuzzTestCase(FailedTestCase, FuzzResult):
    pass


@dataclass(frozen=True)
class BrokenTestSuite(TestResult):
    test_case_names: List[str]
    exception: BaseException

    def format(self) -> str:
        first_line: List[str] = []
        first_line.append(f"[{log_color_provider.colorize('RED', 'BROKEN')}]")
        first_line.append(f"{_get_formatted_file_path(self.file_path)}")
        result = [" ".join(first_line)]
        result.append(str(self.exception))
        return "\n".join(result)


@dataclass(frozen=True)
class UnexpectedExceptionTestSuiteResult(BrokenTestSuite):
    traceback: Optional[str] = None

    def format(self) -> str:
        lines: List[str] = []
        main_line: List[str] = []
        main_line.append(
            f"[{log_color_provider.colorize('RED', 'UNEXPECTED_EXCEPTION')}]"
        )
        main_line.append(_get_formatted_file_path(self.file_path))
        lines.append(" ".join(main_line))

        if self.traceback:
            lines.append(self.traceback)

        lines.append(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        lines.append(str(self.exception))
        return "\n".join(lines)


def _get_formatted_metadata(metadata: ExceptionMetadata) -> str:
    return f"[{metadata.name}]:\n{metadata.format()}"


def _get_formatted_stdout(captured_stdout: Dict[OutputName, str]) -> List[str]:
    result: List[str] = []

    if len(captured_stdout) == 0 or all(
        len(val) == 0 for _, val in captured_stdout.items()
    ):
        return []

    result.append(f"\n[{log_color_provider.colorize('CYAN', 'captured stdout')}]:\n")

    for name, value in captured_stdout.items():
        if value:
            result.append(
                f"[{format_output_name(name)}]:\n{log_color_provider.colorize('GRAY', value)}\n"
            )

    return result


def _get_formatted_file_path(file_path: Path) -> str:
    return log_color_provider.colorize("GRAY", str(file_path))


def _get_formatted_execution_time(execution_time: float) -> str:
    return f"time={log_color_provider.bold(f'{execution_time:.2f}')}s"
