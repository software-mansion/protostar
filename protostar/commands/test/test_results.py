from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from typing_extensions import Self

from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputName


@dataclass
class TestExecutionResult:
    execution_resources: Optional[ExecutionResourcesSummary]


@dataclass
class FuzzTestExecutionResult(TestExecutionResult):
    fuzz_runs_count: int


@dataclass(frozen=True)
class TestResult:
    file_path: Path


@dataclass(frozen=True)
class TestCaseResult(TestResult):
    test_case_name: str
    captured_stdout: Dict[OutputName, str]


@dataclass(frozen=True)
class TimedTestResult:
    execution_time: float


@dataclass(frozen=True)
class PassedTestCaseResult(TestCaseResult, TimedTestResult):
    execution_resources: Optional[ExecutionResourcesSummary]

    @classmethod
    def from_test_execution_result(
        cls,
        test_execution_result: TestExecutionResult,
        **kwargs,
    ) -> Self:
        return cls(
            execution_resources=test_execution_result.execution_resources,
            **kwargs,
        )


@dataclass(frozen=True)
class FailedTestCaseResult(TestCaseResult, TimedTestResult):
    exception: ReportedException

    @classmethod
    def from_reported_exception(
        cls,
        exception: ReportedException,
        **kwargs,
    ) -> Self:
        return cls(
            exception=exception,
            **kwargs,
        )


@dataclass(frozen=True)
class FuzzResult:
    fuzz_runs_count: Optional[int]


@dataclass(frozen=True)
class PassedFuzzTestCaseResult(PassedTestCaseResult, FuzzResult):
    @classmethod
    def from_test_execution_result(
        cls,
        test_execution_result: TestExecutionResult,
        **kwargs,
    ) -> Self:
        if isinstance(test_execution_result, FuzzTestExecutionResult):
            fuzz_runs_count = test_execution_result.fuzz_runs_count
        else:
            fuzz_runs_count = None

        return cls(
            execution_resources=test_execution_result.execution_resources,
            fuzz_runs_count=fuzz_runs_count,
            **kwargs,
        )


@dataclass(frozen=True)
class FailedFuzzTestCaseResult(FailedTestCaseResult, FuzzResult):
    @classmethod
    def from_reported_exception(cls, exception: ReportedException, **kwargs) -> Self:
        fuzz_result = cls._extract_fuzz_result_from_reported_exception(exception)
        fuzz_runs_count = fuzz_result.fuzz_runs_count if fuzz_result else None

        return cls(
            exception=exception,
            fuzz_runs_count=fuzz_runs_count,
            **kwargs,
        )

    @staticmethod
    def _extract_fuzz_result_from_reported_exception(
        reported_exception: ReportedException,
    ) -> Optional[FuzzResult]:
        metadata = reported_exception.metadata

        if len(metadata) > 0 and isinstance(metadata[0], FuzzInputExceptionMetadata):
            fuzz_runs_count = reported_exception.execution_info["fuzz_runs"]
            assert isinstance(fuzz_runs_count, int)
            return FuzzResult(fuzz_runs_count)

        return None


@dataclass(frozen=True)
class BrokenTestSuiteResult(TestResult):
    test_case_names: List[str]
    exception: BaseException


@dataclass(frozen=True)
class UnexpectedBrokenTestSuiteResult(BrokenTestSuiteResult):
    traceback: Optional[str]
