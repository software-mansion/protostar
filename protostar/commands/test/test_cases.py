from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from typing_extensions import Protocol

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
    def accept(self, visitor: "TestResultVisitor") -> None:
        ...


# pylint: disable=abstract-method
@dataclass(frozen=True)
class TestCaseResult(TestResult):
    test_case_name: str
    captured_stdout: Dict[OutputName, str]


@dataclass(frozen=True)
class PassedTestCaseResult(TestCaseResult):
    execution_resources: Optional[ExecutionResourcesSummary]
    execution_time: float
    fuzz_runs_count: Optional[int] = None

    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_passed_test_case_result(self)


@dataclass(frozen=True)
class FailedTestCaseResult(TestCaseResult):
    exception: ReportedException
    execution_time: float

    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_failed_test_case_result(self)


@dataclass(frozen=True)
class FuzzResult:
    fuzz_runs_count: Optional[int]


@dataclass(frozen=True)
class PassedFuzzTestCaseResult(PassedTestCaseResult, FuzzResult):
    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_passed_fuzz_test_case_result(self)


@dataclass(frozen=True)
class FailedFuzzTestCaseResult(FailedTestCaseResult, FuzzResult):
    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_failed_fuzz_test_case_result(self)


@dataclass(frozen=True)
class BrokenTestSuiteResult(TestResult):
    test_case_names: List[str]
    exception: BaseException

    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_broken_test_suite_result(self)

    def format(self) -> str:
        first_line: List[str] = []
        first_line.append(f"[{log_color_provider.colorize('RED', 'BROKEN')}]")
        first_line.append(f"{_get_formatted_file_path(self.file_path)}")
        result = [" ".join(first_line)]
        result.append(str(self.exception))
        return "\n".join(result)


@dataclass(frozen=True)
class UnexpectedExceptionTestSuiteResult(BrokenTestSuiteResult):
    traceback: Optional[str] = None

    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_unexpected_exception_test_suite_result(self)

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


class TestResultVisitor(Protocol):
    def visit_passed_test_case_result(
        self, passed_test_case_result: PassedTestCaseResult
    ):
        ...

    def visit_failed_test_case_result(
        self, failed_test_case_result: FailedTestCaseResult
    ):
        ...

    def visit_passed_fuzz_test_case_result(
        self, passed_fuzz_test_case_result: PassedFuzzTestCaseResult
    ):
        ...

    def visit_failed_fuzz_test_case_result(
        self, failed_fuzz_test_case_result: FailedFuzzTestCaseResult
    ):
        ...

    def visit_broken_test_suite_result(
        self, broken_test_suite_result: BrokenTestSuiteResult
    ):
        ...

    def visit_unexpected_exception_test_suite_result(
        self,
        unexpected_exception_test_suite_result: UnexpectedExceptionTestSuiteResult,
    ):
        ...
