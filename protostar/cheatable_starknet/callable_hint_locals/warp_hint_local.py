from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.starknet import Address


class WarpHintLocal(CallableHintLocal):
    @property
    def name(self) -> str:
        return "warp"

    def _build(self):
        return self.warp

    def warp(
        self,
        target_contract_address: int,
        blk_timestamp: int,
    ) -> None:
        self.controllers.block_info.cheat(
            contract_address=Address.from_user_input(target_contract_address),
            block_timestamp=blk_timestamp,
        )
