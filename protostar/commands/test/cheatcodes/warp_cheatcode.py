from typing import Any, Callable, Optional

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.starkware.types import AddressType


class WarpCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "warp"

    def build(self) -> Callable[..., Any]:
        return self.warp

    def warp(
        self, block_timestamp: int, contract_address: Optional[AddressType] = None
    ) -> Callable[[], None]:
        contract_address = contract_address or self.contract_address
        self.state.contract_address_to_block_timestamp[
            contract_address
        ] = block_timestamp

        def stop_warp():
            del self.state.contract_address_to_block_timestamp[contract_address]

        return stop_warp
