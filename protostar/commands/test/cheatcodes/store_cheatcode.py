from typing import Any, Callable, List, Optional
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.storage_var import calc_address


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

        pre_run_contract_carried_state = self.state.contract_states[
            target_contract_address
        ]
        contract_state = pre_run_contract_carried_state.state
        contract_state.assert_initialized(contract_address=target_contract_address)

        starknet_storage = BusinessLogicStarknetStorage(
            commitment_tree=contract_state.storage_commitment_tree,
            ffc=self.state.ffc,
            # Pass a copy of the carried storage updates (instead of a reference) - note that
            # pending_modifications may be modified during the run as a result of an internal call.
            pending_modifications=dict(pre_run_contract_carried_state.storage_updates),
        )

        self._write_on_remote_storage(
            starknet_storage, target_contract_address, variable_address, value
        )

        # Apply modifications to the contract storage.
        self.state.update_contract_storage(
            contract_address=target_contract_address,
            modifications=starknet_storage.get_modifications(),
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
            self.state.modified_contracts[contract] = None
