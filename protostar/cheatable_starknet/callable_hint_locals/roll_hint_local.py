from typing import Any, Callable

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers import BlockInfoController
from protostar.starknet import Address


class RollHintLocal(CallableHintLocal):
    def __init__(self, block_info_controller: BlockInfoController):
        self._block_info_controller = block_info_controller

    @property
    def name(self) -> str:
        return "roll"

    def _build(self) -> Callable[..., Any]:
        return self.roll

    def roll(
        self,
        target_contract_address: int,
        blk_number: int,
    ) -> None:
        self._block_info_controller.set_block_number(
            contract_address=Address.from_user_input(target_contract_address),
            block_number=blk_number,
        )
