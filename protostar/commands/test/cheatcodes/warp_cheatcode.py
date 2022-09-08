from typing import Any, Callable, Optional

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.types import AddressType


class WarpCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "warp"

    def build(self) -> Callable[..., Any]:
        return self.warp

    def warp(
        self,
        blk_timestamp: int,
        target_contract_address: Optional[AddressType] = None,
    ) -> Callable[[], None]:
        target_contract_address = target_contract_address or self.contract_address
        self.cheatable_state.contract_address_to_block_timestamp[
            target_contract_address
        ] = blk_timestamp

        def stop_warp():
            del self.cheatable_state.contract_address_to_block_timestamp[
                target_contract_address
            ]

        return stop_warp
