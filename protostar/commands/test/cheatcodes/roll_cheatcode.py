from typing import Any, Callable, Optional

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.types import AddressType


class RollCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "roll"

    def build(self) -> Callable[..., Any]:
        return self.roll

    def roll(
        self,
        blk_number: int,
        target_contract_address: Optional[AddressType] = None,
    ) -> Callable[[], None]:
        # TODO
        # target_contract_address = target_contract_address or self.contract_address
        return self.cheatable_state.cheat_block_info(block_number=blk_number)
