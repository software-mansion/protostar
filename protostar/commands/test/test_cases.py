from pathlib import Path
from typing import List, Optional

from attr import dataclass
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.utils.log_color_provider import log_color_provider


@dataclass(frozen=True)
class TestCaseResult:
    file_path: Path

    def get_formatted_file_path(self):
        return log_color_provider.colorize("GRAY", str(self.file_path))


@dataclass(frozen=True)
class PassedTestCase(TestCaseResult):
    function_name: str
    tx_info: Optional[StarknetTransactionExecutionInfo]

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('GREEN', 'PASS')}]")
        result.append(f"{self.get_formatted_file_path()} {self.function_name}")
        return " ".join(result)


@dataclass(frozen=True)
class FailedTestCase(TestCaseResult):
    function_name: str
    exception: ReportedException

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('RED', 'FAIL')}] ")
        result.append(f"{self.get_formatted_file_path()} {self.function_name}")
        result.append("\n")
        result.append(str(self.exception))
        result.append("\n")
        return "".join(result)


@dataclass(frozen=True)
class BrokenTestSuite(TestCaseResult):
    exception: StarkException

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('RED', 'BROKEN')}]")
        result.append(f"{self.get_formatted_file_path()}")
        return " ".join(result)
