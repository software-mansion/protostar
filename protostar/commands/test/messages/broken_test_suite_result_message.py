from pathlib import Path
from dataclasses import dataclass

from protostar.io import LogColorProvider

from .test_case_result_message import TestCaseResultMessage



@dataclass
class BrokenTestSuiteResult(TestCaseResultMessage):
    test_suite_path: Path
    exception: str

    status = "broken"
    type = "test_case_result"

    def format_human(self, fmt: LogColorProvider) -> str:
        pass

    def format_dict(self) -> dict:
        return {
          "type": self.type,
          "status": self.status,
          "test_suite_path": str(self.test_suite_path),
          "exception": self.exception,
        }
