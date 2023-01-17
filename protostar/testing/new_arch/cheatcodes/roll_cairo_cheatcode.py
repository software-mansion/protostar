from typing import Any, Callable

from protostar.starknet import RawAddress, Address
from protostar.testing.new_arch.cheatcodes.cairo_cheatcode import CairoCheatcode


class RollCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "roll"

    def build(self) -> Callable[..., Any]:
        return self.roll

    def roll(
        self,
        target_contract_address: RawAddress,
        blk_number: int,
    ) -> Callable[[], None]:
        return self.cheaters.block_info.cheat(
            contract_address=Address.from_user_input(target_contract_address),
            block_number=blk_number,
        )
