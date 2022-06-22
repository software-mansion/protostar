from typing import Any, Callable, Optional

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.starkware.types import AddressType


class RollCheatcode(Cheatcode):
    @staticmethod
    def name() -> str:
        return "roll"

    def build(self) -> Callable[..., Any]:
        return self.roll

    def roll(
        self, block_number: int, contract_address: Optional[AddressType] = None
    ) -> Callable[[], None]:
        contract_address = contract_address or self.contract_address
        self.state.contract_address_to_block_number[contract_address] = block_number

        def stop_warp():
            del self.state.contract_address_to_block_number[contract_address]

        return stop_warp
