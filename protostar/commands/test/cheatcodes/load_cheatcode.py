from typing import Any, Callable, List, Optional

from starkware.starknet.business_logic.state.state import ContractStorageState

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
        return self.load_remote(
            target_contract_address, variable_address, variable_size
        )

    def load_remote(
        self, target_contract_address: int, variable_address: int, variable_size: int
    ) -> List[int]:
        """
        This function closely emulates a behaviour of calling an external method which returns storage_var state.
        """

        starknet_storage = ContractStorageState(
            state=self.sync_state, contract_address=target_contract_address
        )

        # Perform syscall on the contract state
        result = self._load_from_remote_storage(
            starknet_storage, variable_address, variable_size
        )
        return result

    def load_local(self, address: int, size: int) -> List[int]:
        return [self._storage_read(address=address + i) for i in range(size)]

    def variable_size(self, contract_address: int, variable_type: str) -> int:
        if variable_type == "felt":
            return 1
        abi = self.cheatable_state.get_abi_from_contract_address(contract_address)

        abi_type = next((el for el in abi if el["name"] == variable_type), None)
        if not abi_type or not "size" in abi_type:
            raise CheatcodeException(
                self,
                f"Type {variable_type} has not been found in contract {contract_address}",
            )

        return abi_type["size"]

    @staticmethod
    def _load_from_remote_storage(storage, address: int, size: int) -> List[int]:
        return [storage.read(address=address + i) for i in range(size)]
