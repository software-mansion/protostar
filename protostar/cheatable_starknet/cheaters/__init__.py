from dataclasses import dataclass

from .block_info import BlockInfoCairoCheater
from .contracts import ContractsCairoCheater
from .expects import ExpectsCairoCheater


@dataclass(frozen=True)
class CairoCheaters:
    block_info: BlockInfoCairoCheater
    contracts: ContractsCairoCheater
    expects: ExpectsCairoCheater
