from typing import Any, Callable, List, Optional
from starkware.starknet.storage.starknet_storage import BusinessLogicStarknetStorage
from protostar.commands.test.test_environment_exceptions import CheatcodeException

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.storage_var import calc_address


class LoadCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "load"

    def build(self) -> Callable[..., Any]:
        return self.load

    def load(
        self,
        target_contract_address: int,
        variable_name: str,
        variable_type: str,
        key: Optional[List[int]] = None,
    ) -> List[int]:
        key = key or []
        variable_address = calc_address(variable_name, key)
        variable_size = self.variable_size(target_contract_address, variable_type)

        if target_contract_address == self.contract_address:
            return self.load_local(variable_address, variable_size)

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

        result = self._load_from_remote_storage(
            starknet_storage, variable_address, variable_size
        )

        # Apply modifications to the contract storage.
        self.state.update_contract_storage(
            contract_address=target_contract_address,
            modifications=starknet_storage.get_modifications(),
        )
        return result

    def load_local(self, address: int, size: int) -> List[int]:
        return [self._storage_read(address=address + i) for i in range(size)]

    def variable_size(self, contract_address: int, variable_type: str) -> int:
        if variable_type == "felt":
            return 1
        abi = self.state.get_abi_with_contract_address(contract_address)
        abi_type = next(el for el in abi if el["name"] == variable_type)
        if not abi_type or not "size" in abi_type:
            raise CheatcodeException(
                self.name,
                f"Type {variable_type} has not been found in contract {contract_address}",
            )

        return abi_type["size"]

    @staticmethod
    def _load_from_remote_storage(storage, address: int, size: int) -> List[int]:
        return [storage.read(address=address + i) for i in range(size)]
