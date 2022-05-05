from pathlib import Path
from typing import List, Optional

from attr import dataclass
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException

from src.commands.test.test_environment_exceptions import ReportedException
from src.utils.log_color_provider import log_color_provider


@dataclass(frozen=True)
class CaseResult:
    file_path: Path

    def get_formatted_file_path(self):
        return log_color_provider.colorize("GRAY", str(self.file_path))


@dataclass(frozen=True)
class PassedCase(CaseResult):
    function_name: str
    tx_info: Optional[StarknetTransactionExecutionInfo]

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('GREEN', 'PASS')}]")
        result.append(f"{self.get_formatted_file_path()} {self.function_name}")
        return " ".join(result)


@dataclass(frozen=True)
class FailedCase(CaseResult):
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
class BrokenTest(CaseResult):
    exception: StarkException

    def __str__(self) -> str:
        result: List[str] = []
        result.append(f"[{log_color_provider.colorize('RED', 'BROKEN')}]")
        result.append(f"{self.get_formatted_file_path()}")
        return " ".join(result)
