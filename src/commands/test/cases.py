from pathlib import Path
from typing import Optional

from attr import dataclass
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException


@dataclass
class PassedCase:
    tx_info: Optional[StarknetTransactionExecutionInfo]


@dataclass
class FailedCase:
    file_path: Path
    function_name: str
    exception: BaseException


@dataclass
class BrokenTest:
    file_path: Path
    exception: StarkException
