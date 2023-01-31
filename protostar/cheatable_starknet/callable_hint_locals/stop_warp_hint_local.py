from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.starknet import Address


class StopWarpHintLocal(CallableHintLocal):
    @property
    def name(self) -> str:
        return "stop_warp"

    def _build(self):
        return self.stop_warp

    def stop_warp(
        self,
        target_contract_address: int,
    ):
        self.controllers.block_info.clear_block_timestamp_cheat(
            contract_address=Address.from_user_input(target_contract_address)
        )
