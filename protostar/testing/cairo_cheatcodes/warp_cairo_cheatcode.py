from typing import Callable

from protostar.starknet import RawAddress, Address
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet.forkable_starknet import ForkableStarknet


class WarpCairoCheatcode(CairoCheatcode):
    def __init__(self, starknet: ForkableStarknet) -> None:
        super().__init__()
        self._starknet = starknet

    @property
    def name(self) -> str:
        return "warp"

    def build(self):
        return self.warp

    def warp(
        self,
        blk_timestamp: int,
        target_contract_address: RawAddress,
    ) -> Callable[[], None]:
        return self._starknet.cheaters.block_info.cheat(
            contract_address=Address.from_user_input(target_contract_address),
            block_timestamp=blk_timestamp,
        )
