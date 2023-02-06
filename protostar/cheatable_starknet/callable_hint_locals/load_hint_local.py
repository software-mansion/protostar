import asyncio
from typing import Optional, List

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers import StorageController


class LoadHintLocal(CallableHintLocal):
    def __init__(self, storage_controller: StorageController):
        self._storage_controller = storage_controller

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
            self._storage_controller.load(
                target_contract_address=target_contract_address,
                variable_name=variable_name,
                variable_type=variable_type,
                key=key,
            )
        )
