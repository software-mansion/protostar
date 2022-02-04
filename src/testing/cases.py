from pathlib import Path

from attr import dataclass
from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException


@dataclass
class PassedCase:
    tx_info: StarknetTransactionExecutionInfo


@dataclass
class FailedCase:
    file_path: Path
    function_name: str
    exception: StarkException


@dataclass
class BrokenTest:
    file_path: Path
    exception: StarkException
