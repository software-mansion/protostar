from dataclasses import dataclass

from protostar.cheatable_starknet.controllers.block_info import BlockInfoController
from protostar.cheatable_starknet.controllers.contracts import ContractsController
from protostar.cheatable_starknet.controllers.storage import StorageController


@dataclass(frozen=True)
class Controllers:
    block_info: BlockInfoController
    contracts: ContractsController
    storage: StorageController
