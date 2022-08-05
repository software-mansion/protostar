from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from typing_extensions import Protocol

from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputName


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


@dataclass(frozen=True)
class UnexpectedExceptionTestSuiteResult(BrokenTestSuiteResult):
    traceback: Optional[str]

    def accept(self, visitor: "TestResultVisitor") -> None:
        return visitor.visit_unexpected_exception_test_suite_result(self)


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
