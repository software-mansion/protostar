from dataclasses import dataclass

from protostar.starknet.new_arch.cheaters.block_info import BlockInfoCairoCheater
from protostar.starknet.new_arch.cheaters.contracts import ContractsCairoCheater


@dataclass(frozen=True)
class CairoCheaters:
    block_info: BlockInfoCairoCheater
    contracts: ContractsCairoCheater
