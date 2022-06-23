from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from protostar.commands.test.starkware.execution_resources_facade import (
    ExecutionResourcesFacade,
)
from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG
from protostar.utils.log_color_provider import log_color_provider


@dataclass(frozen=True)
class TestCaseResult:
    file_path: Path

    def get_formatted_file_path(self):
        return log_color_provider.colorize("GRAY", str(self.file_path))


@dataclass(frozen=True)
class PassedTestCase(TestCaseResult):
    test_case_name: str
    execution_resources: Optional[ExecutionResourcesFacade]

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('GREEN', 'PASS')}]")
        result.append(f"{self.get_formatted_file_path()} {self.test_case_name}")
        # TODO: refine
        result.append("")
        result.append(str(self.execution_resources))
        return " ".join(result)


@dataclass(frozen=True)
class FailedTestCase(TestCaseResult):
    test_case_name: str
    exception: ReportedException

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('RED', 'FAIL')}] ")
        result.append(f"{self.get_formatted_file_path()} {self.test_case_name}")
        result.append("\n")
        result.append(str(self.exception))
        result.append("\n")
        return "".join(result)


@dataclass(frozen=True)
class BrokenTestSuite(TestCaseResult):
    test_case_names: List[str]
    exception: BaseException

    def __str__(self) -> str:
        first_line: List[str] = []
        first_line.append(f"[{log_color_provider.colorize('RED', 'BROKEN')}]")
        first_line.append(f"{self.get_formatted_file_path()}")
        result = [" ".join(first_line)]
        result.append(str(self.exception))
        return "\n".join(result)


@dataclass(frozen=True)
class UnexpectedExceptionTestSuiteResult(BrokenTestSuite):
    def __str__(self) -> str:
        first_line: List[str] = []
        first_line.append(
            f"[{log_color_provider.colorize('RED', 'UNEXPECTED_EXCEPTION')}]"
        )
        first_line.append(self.get_formatted_file_path())

        result = [" ".join(first_line), UNEXPECTED_PROTOSTAR_ERROR_MSG]
        result.append(str(self.exception))
        return "\n".join(result)
