from typing import Callable

from protostar.starknet.address import Address
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode


class PrankCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "prank"

    def build(self) -> Callable:
        return self.prank

    def prank(self, caller_address: int, target_contract_address: int):
        return self.cheaters.contracts.prank(
            caller_address=Address.from_user_input(caller_address),
            target_address=Address.from_user_input(target_contract_address),
        )
