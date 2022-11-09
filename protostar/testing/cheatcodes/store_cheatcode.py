from typing import Any, Callable, List, Optional

from starkware.starknet.business_logic.state.state import ContractStorageState

from protostar.starknet import Cheatcode, calc_address

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
            storage=starknet_storage,
            variable_address=variable_address,
            value=value,
        )

    def store_local(self, address: int, value: List[int]):
        for i, val in enumerate(value):
            self._storage_write(address=address + i, value=val)

    def _write_on_remote_storage(
        self, storage: ContractStorageState, variable_address: int, value: List[int]
    ):
        for i, val in enumerate(value):
            storage.read(address=variable_address + i)
            storage.write(address=variable_address + i, value=val)
