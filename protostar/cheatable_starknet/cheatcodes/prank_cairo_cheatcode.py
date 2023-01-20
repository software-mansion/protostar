from typing import Callable

from protostar.starknet import Address
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode


class PrankCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "prank"

    def _build(self) -> Callable:
        return self.prank

    def prank(self, caller_address: int, target_address: int):
        valid_target_address = Address.from_user_input(target_address)
        self.cheaters.contracts.prank(
            caller_address=Address.from_user_input(caller_address),
            target_address=valid_target_address,
        )
        return lambda: self.cheaters.contracts.cancel_prank(
            target_address=valid_target_address
        )
