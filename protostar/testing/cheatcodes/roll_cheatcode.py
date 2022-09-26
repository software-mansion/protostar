from typing import Any, Callable, Optional

from protostar.starknet import AddressType, Cheatcode


class RollCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "roll"

    def build(self) -> Callable[..., Any]:
        return self.roll

    def roll(
        self,
        blk_number: int,
        target_contract_address: Optional[AddressType] = None,
    ) -> Callable[[], None]:
        target_contract_address = target_contract_address or self.contract_address
        return self.cheaters.block_info.cheat(
            contract_address=target_contract_address,
            block_number=blk_number,
        )
