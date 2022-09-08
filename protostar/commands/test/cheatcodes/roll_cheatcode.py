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
        self, blk_number: int, target_contract_address: Optional[AddressType] = None
    ) -> Callable[[], None]:
        target_contract_address = target_contract_address or self.contract_address
        self.cheatable_state.contract_address_to_block_number[
            target_contract_address
        ] = blk_number

        def stop_warp():
            del self.cheatable_state.contract_address_to_block_number[
                target_contract_address
            ]

        return stop_warp
