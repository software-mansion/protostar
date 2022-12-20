from pathlib import Path
from dataclasses import dataclass

from protostar.io import LogColorProvider

from .test_case_result_message import TestCaseResultMessage


@dataclass
class SkippedTestCaseResult(TestCaseResultMessage):
    test_suite_path: Path
    test_case_name: str

    reason: str

    status = "skipped"
    type = "test_case_result"

    def format_human(self, fmt: LogColorProvider) -> str:
        pass

    def format_dict(self) -> dict:
        return {
          "type": self.type,
          "status": self.status,
          "test_suite_path": str(self.test_suite_path),
          "test_case_name": self.test_case_name,
          "reason": self.reason,
        }
