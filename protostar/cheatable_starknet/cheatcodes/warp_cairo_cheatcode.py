from typing import Callable

from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet import RawAddress, Address


class WarpCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "warp"

    def build(self):
        return self.warp

    def warp(
        self,
        target_contract_address: RawAddress,
        blk_timestamp: int,
    ) -> Callable[[], None]:
        return self.cheaters.block_info.cheat(
            contract_address=Address.from_user_input(target_contract_address),
            block_timestamp=blk_timestamp,
        )
