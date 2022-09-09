from typing import Any, Callable, List, Optional
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.storage_var import calc_address
from starkware.starknet.business_logic.state.state import ContractStorageState

ADDR_BOUND = 2**251 - 256


class StoreCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "store"

    def build(self) -> Callable[..., Any]:
        return self.store

    def store(
        self,
        target_contract_address: int,
        variable_name: str,
        value: List[int],
        key: Optional[List[int]] = None,
    ):
        key = key or []
        variable_address = calc_address(variable_name, key)
        if target_contract_address == self.contract_address:
            self.store_local(variable_address, value)
            return

        starknet_storage = ContractStorageState(
            state=self.sync_state, contract_address=target_contract_address
        )

        self._write_on_remote_storage(
            starknet_storage, target_contract_address, variable_address, value
        )

    def store_local(self, address: int, value: List[int]):
        for i, val in enumerate(value):
            self._storage_write(address=address + i, value=val)

    def _write_on_remote_storage(
        self, storage, contract, address: int, value: List[int]
    ):
        for i, val in enumerate(value):
            storage.read(address=address + i)
            storage.write(address=address + i, value=val)
            self.resources_manager.modified_contracts[self.contract_address] = None
