import asyncio
from typing import Optional

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
        value: list[int],
        key: Optional[list[int]] = None,
    ):
        asyncio.run(
            self.controllers.storage.store(
                target_contract_address=target_contract_address,
                variable_name=variable_name,
                value=value,
                key=key,
            )
        )
