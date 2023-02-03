import asyncio
from typing import Optional, List

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)


class LoadHintLocal(CallableHintLocal):
    @property
    def name(self) -> str:
        return "load"

    def _build(self):
        return self.load

    def load(
        self,
        target_contract_address: int,
        variable_name: str,
        variable_type: str,
        key: Optional[List[int]] = None,
    ) -> List[int]:
        return asyncio.run(
            self.controllers.storage.load(
                target_contract_address=target_contract_address,
                variable_name=variable_name,
                variable_type=variable_type,
                key=key,
            )
        )
