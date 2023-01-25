from dataclasses import dataclass

from protostar.cheatable_starknet.cheaters.block_info import BlockInfoCairoCheater
from protostar.cheatable_starknet.cheaters.contracts import ContractsCairoCheater
from protostar.cheatable_starknet.cheaters.storage import StorageCairoCheater


@dataclass(frozen=True)
class CairoCheaters:
    block_info: BlockInfoCairoCheater
    contracts: ContractsCairoCheater
    storage: StorageCairoCheater
