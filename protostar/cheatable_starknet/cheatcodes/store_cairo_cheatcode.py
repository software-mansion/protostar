import asyncio
from typing import List, Optional

from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode


class StoreCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "store"

    def _build(self):
        return self.store

    def store(
        self,
        target_contract_address: int,
        variable_name: str,
        value: List[int],
        key: Optional[List[int]] = None,
    ):
        asyncio.run(
            self.cheaters.storage.store(
                target_contract_address=target_contract_address,
                variable_name=variable_name,
                value=value,
                key=key,
            )
        )
