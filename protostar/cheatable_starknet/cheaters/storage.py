from typing import List, Optional, TYPE_CHECKING, Set

from starkware.starknet.business_logic.state.state_api import State

from protostar.starknet import calc_address, BreakingReportedException

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatable_cached_state import CheatableCachedState


class AsyncContractStorageState:
    """
    Defines the API for accessing StarkNet single contract storage state.
    """

    def __init__(self, state: State, contract_address: int):
        self.state = state
        self.contract_address = contract_address

        # Maintain all read request values in chronological order.
        self.read_values: List[int] = []
        self.accessed_keys: Set[int] = set()

    async def read(self, address: int) -> int:
        self.accessed_keys.add(address)
        value = await self.state.get_storage_at(
            contract_address=self.contract_address, key=address
        )
        self.read_values.append(value)

        return value

    async def write(self, address: int, value: int):
        self.accessed_keys.add(address)
        await self.state.set_storage_at(
            contract_address=self.contract_address, key=address, value=value
        )


class StorageCairoCheater:
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    async def store(
        self,
        target_contract_address: int,
        variable_name: str,
        value: List[int],
        key: Optional[List[int]] = None,
    ):
        key = key or []
        variable_address = calc_address(variable_name, key)
        contract_storage = AsyncContractStorageState(
            state=self.cheatable_state,
            contract_address=target_contract_address,
        )

        for i, val in enumerate(value):
            await contract_storage.read(address=variable_address + i)
            await contract_storage.write(address=variable_address + i, value=val)

    async def load(
        self,
        target_contract_address: int,
        variable_name: str,
        variable_type: str,
        key: Optional[List[int]] = None,
    ) -> List[int]:
        key = key or []
        variable_address = calc_address(variable_name, key)
        variable_size = self._get_variable_size(target_contract_address, variable_type)

        starknet_storage = AsyncContractStorageState(
            state=self.cheatable_state,
            contract_address=target_contract_address,
        )

        return [
            await starknet_storage.read(address=variable_address + i)
            for i in range(variable_size)
        ]

    def _get_variable_size(self, contract_address: int, variable_type: str) -> int:
        if variable_type == "felt":
            return 1
        abi = self.cheatable_state.get_abi_from_contract_address(contract_address)

        abi_type = next((el for el in abi if el["name"] == variable_type), None)
        if not abi_type or "size" not in abi_type:
            raise BreakingReportedException(
                f"Type {variable_type} has not been found in contract {contract_address}",
            )

        return abi_type["size"]
