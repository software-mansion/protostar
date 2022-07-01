from typing import Any, Callable, List, Optional
from starkware.starknet.public.abi import get_storage_var_address
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage
from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash

from protostar.commands.test.starkware.cheatcode import Cheatcode


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
        var: str,
        value: List[int],
        key: Optional[List[int]] = None,
    ):
        key = key or []
        variable_address = self.calc_address(var, key)
        if target_contract_address == self.contract_address:
            for i, val in enumerate(value):
                self.store_local(variable_address + i, val)
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
            loop=self.loop,
        )

        for i, val in enumerate(value):
            self._write_on_remote_storage(
                starknet_storage, target_contract_address, variable_address + i, val
            )

        # Apply modifications to the contract storage.
        self.state.update_contract_storage(
            contract_address=target_contract_address,
            modifications=starknet_storage.get_modifications(),
        )

    def store_local(self, address: int, value: int):
        self._storage_write(address=address, value=value)

    def _write_on_remote_storage(self, storage, contract, address: int, value: int):
        storage.read(address=address)
        storage.write(address=address, value=value)

        self.state.modified_contracts[contract] = None

    @staticmethod
    def calc_address(var, key) -> int:
        res = get_storage_var_address(var)
        for i in key:
            res = pedersen_hash(res, i)
        if len(key) > 0:
            res = StoreCheatcode.normalize_address(res)
        return res

    @staticmethod
    def normalize_address(addr: int) -> int:
        return addr if addr < ADDR_BOUND else addr - ADDR_BOUND
