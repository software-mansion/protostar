from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.test_output_recorder import OutputName


@dataclass(frozen=True)
class TestResult:
    file_path: Path


# pylint: disable=abstract-method
@dataclass(frozen=True)
class TestCaseResult(TestResult):
    test_case_name: str
    captured_stdout: Dict[OutputName, str]


@dataclass(frozen=True)
class PassedTestCaseResult(TestCaseResult):
    execution_resources: Optional[ExecutionResourcesSummary]
    execution_time: float


@dataclass(frozen=True)
class FailedTestCaseResult(TestCaseResult):
    exception: ReportedException
    execution_time: float


@dataclass(frozen=True)
class FuzzResult:
    fuzz_runs_count: Optional[int]


@dataclass(frozen=True)
class PassedFuzzTestCaseResult(PassedTestCaseResult, FuzzResult):
    pass


@dataclass(frozen=True)
class FailedFuzzTestCaseResult(FailedTestCaseResult, FuzzResult):
    pass


@dataclass(frozen=True)
class BrokenTestSuiteResult(TestResult):
    test_case_names: List[str]
    exception: BaseException


@dataclass(frozen=True)
class UnexpectedExceptionTestSuiteResult(BrokenTestSuiteResult):
    traceback: Optional[str]
