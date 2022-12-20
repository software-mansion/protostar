from pathlib import Path
from dataclasses import dataclass

from protostar.io import LogColorProvider
from protostar.testing import OutputName

from .test_case_result_message import (
  TestCaseResultMessage,
  get_formatted_execution_time,
)


@dataclass
class PassedTestCaseResult(TestCaseResultMessage):
    test_suite_path: Path
    test_case_name: str
    execution_time_in_seconds: float
    stdout: dict[OutputName, str]

    status = "passed"
    type = "test_case_result"

    def format_human(self, fmt: LogColorProvider) -> str:
        pass

    def format_dict(self) -> dict:
        return {
          "type": self.type,
          "status": self.status,
          "test_suite_path": str(self.test_suite_path),
          "test_case_name": self.test_case_name,
          "execution_time_in_seconds": get_formatted_execution_time(self.execution_time_in_seconds),
          "stdout": str(self.stdout),
        }
