from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers import BlockInfoController
from protostar.starknet import Address


class StartWarpHintLocal(CallableHintLocal):
    def __init__(self, block_info_controller: BlockInfoController):
        self._block_info_controller = block_info_controller

    @property
    def name(self) -> str:
        return "start_warp"

    def _build(self):
        return self.start_warp

    def start_warp(
        self,
        target_contract_address: int,
        block_timestamp: int,
    ) -> None:
        self._block_info_controller.set_block_timestamp(
            contract_address=Address.from_user_input(target_contract_address),
            block_timestamp=block_timestamp,
        )
