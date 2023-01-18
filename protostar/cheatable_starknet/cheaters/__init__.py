from dataclasses import dataclass

from protostar.cheatable_starknet.cheaters.block_info import BlockInfoCairoCheater
from protostar.cheatable_starknet.cheaters.contracts import ContractsCairoCheater


@dataclass(frozen=True)
class CairoCheaters:
    block_info: BlockInfoCairoCheater
    contracts: ContractsCairoCheater
