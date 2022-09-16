from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from typing_extensions import Self

from protostar.commands.test.test_environment_exceptions import ReportedException

from .starkware.execution_resources_summary import ExecutionResourcesSummary
from .test_output_recorder import OutputName


@dataclass(frozen=True)
class TestResult:
    file_path: Path


@dataclass(frozen=True)
class TimedTestResult:
    execution_time: float


@dataclass(frozen=True)
class TestCaseResult(TestResult):
    test_case_name: str
    captured_stdout: Dict[OutputName, str]


@dataclass(frozen=True)
class TimedTestCaseResult(TestCaseResult, TimedTestResult):
    pass


@dataclass(frozen=True)
class PassedTestCaseResult(TimedTestCaseResult):
    execution_resources: Optional[ExecutionResourcesSummary]


@dataclass(frozen=True)
class FailedTestCaseResult(TimedTestCaseResult):
    exception: ReportedException


@dataclass(frozen=True)
class BrokenTestCaseResult(TimedTestCaseResult):
    exception: ReportedException


@dataclass(frozen=True)
class SkippedTestCaseResult(TimedTestCaseResult):
    reason: Optional[str]


@dataclass(frozen=True)
class FuzzResult:
    fuzz_runs_count: Optional[int]


@dataclass(frozen=True)
class PassedFuzzTestCaseResult(PassedTestCaseResult, FuzzResult):
    @classmethod
    def from_passed_test_case_result(
        cls, passed_test_case_result: PassedTestCaseResult, fuzz_result: FuzzResult
    ) -> Self:
        return cls(
            file_path=passed_test_case_result.file_path,
            test_case_name=passed_test_case_result.test_case_name,
            captured_stdout=passed_test_case_result.captured_stdout,
            execution_resources=passed_test_case_result.execution_resources,
            execution_time=passed_test_case_result.execution_time,
            fuzz_runs_count=fuzz_result.fuzz_runs_count,
        )


@dataclass(frozen=True)
class FailedFuzzTestCaseResult(FailedTestCaseResult, FuzzResult):
    @classmethod
    def from_failed_test_case_result(
        cls,
        failed_test_case_result: FailedTestCaseResult,
        fuzz_result: Optional[FuzzResult],
    ) -> Self:
        fuzz_runs_count = fuzz_result.fuzz_runs_count if fuzz_result else None

        return cls(
            file_path=failed_test_case_result.file_path,
            test_case_name=failed_test_case_result.test_case_name,
            captured_stdout=failed_test_case_result.captured_stdout,
            exception=failed_test_case_result.exception,
            execution_time=failed_test_case_result.execution_time,
            fuzz_runs_count=fuzz_runs_count,
        )


@dataclass(frozen=True)
class BrokenFuzzTestCaseResult(BrokenTestCaseResult, FuzzResult):
    @classmethod
    def from_broken_test_case_result(
        cls,
        broken_test_case_result: BrokenTestCaseResult,
        fuzz_result: Optional[FuzzResult],
    ) -> Self:
        fuzz_runs_count = fuzz_result.fuzz_runs_count if fuzz_result else None

        return cls(
            file_path=broken_test_case_result.file_path,
            test_case_name=broken_test_case_result.test_case_name,
            captured_stdout=broken_test_case_result.captured_stdout,
            exception=broken_test_case_result.exception,
            execution_time=broken_test_case_result.execution_time,
            fuzz_runs_count=fuzz_runs_count,
        )


@dataclass(frozen=True)
class SetupCaseResult(TestResult, TimedTestResult):
    test_case_name: str
    setup_case_name: str


@dataclass(frozen=True)
class PassedSetupCaseResult(SetupCaseResult):
    pass


@dataclass(frozen=True)
class BrokenSetupCaseResult(SetupCaseResult):
    captured_stdout: Dict[OutputName, str]
    exception: ReportedException

    def into_broken_test_case_result(self) -> BrokenTestCaseResult:
        return BrokenTestCaseResult(
            file_path=self.file_path,
            test_case_name=self.test_case_name,
            execution_time=self.execution_time,
            captured_stdout=self.captured_stdout,
            exception=self.exception,
        )


@dataclass(frozen=True)
class SkippedSetupCaseResult(SetupCaseResult):
    captured_stdout: Dict[OutputName, str]
    reason: Optional[str]

    def into_skipped_test_case_result(self) -> SkippedTestCaseResult:
        return SkippedTestCaseResult(
            file_path=self.file_path,
            test_case_name=self.test_case_name,
            execution_time=self.execution_time,
            captured_stdout=self.captured_stdout,
            reason=self.reason,
        )


@dataclass(frozen=True)
class BrokenTestSuiteResult(TestResult):
    test_case_names: List[str]
    exception: BaseException


@dataclass(frozen=True)
class UnexpectedBrokenTestSuiteResult(BrokenTestSuiteResult):
    traceback: Optional[str]
