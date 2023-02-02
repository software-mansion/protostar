from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.starknet import Address


class StopRollHintLocal(CallableHintLocal):
    @property
    def name(self) -> str:
        return "stop_roll"

    def _build(self):
        return self.stop_roll

    def stop_roll(
        self,
        target_contract_address: int,
    ):
        self.controllers.block_info.clear_block_number_cheat(
            contract_address=Address.from_user_input(target_contract_address)
        )
