from typing import Any, Callable

from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet import RawAddress, Address


class RollCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "roll"

    def _build(self) -> Callable[..., Any]:
        return self.roll

    def roll(
        self,
        target_contract_address: RawAddress,
        blk_number: int,
    ) -> Callable[[], None]:
        return self.controllers.block_info.cheat(
            contract_address=Address.from_user_input(target_contract_address),
            block_number=blk_number,
        )
