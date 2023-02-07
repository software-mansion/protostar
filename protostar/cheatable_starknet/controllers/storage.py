from typing import List, Optional, TYPE_CHECKING

from protostar.cairo_testing.cairo_test_execution_state import ContractsControllerState
from protostar.starknet import calc_address, BreakingReportedException
from protostar.starknet.address import Address

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


class StorageController:
    def __init__(
        self, state: "ContractsControllerState", cheatable_state: "CheatableCachedState"
    ):
        self._state = state
        self._cheatable_state = cheatable_state

    async def store(
        self,
        target_contract_address: int,
        variable_name: str,
        value: List[int],
        key: Optional[List[int]] = None,
    ):
        variable_address = calc_address(variable_name, key or [])
        for i, val in enumerate(value):
            await self._cheatable_state.set_storage_at(
                contract_address=target_contract_address,
                key=variable_address + i,
                value=val,
            )

    async def load(
        self,
        target_contract_address: int,
        variable_name: str,
        variable_type: str,
        key: Optional[List[int]] = None,
    ) -> List[int]:
        variable_address = calc_address(variable_name, key or [])
        variable_size = self._get_variable_size(target_contract_address, variable_type)

        return [
            await self._cheatable_state.get_storage_at(
                contract_address=target_contract_address, key=variable_address + i
            )
            for i in range(variable_size)
        ]

    def _get_variable_size(self, contract_address: int, variable_type: str) -> int:
        if variable_type == "felt":
            return 1
        abi = self._state.get_contract_abi_from_contract_address(
            Address(contract_address)
        )

        abi_type = next((el for el in abi if el["name"] == variable_type), None)
        if not abi_type or "size" not in abi_type:
            raise BreakingReportedException(
                f"Type {variable_type} has not been found in contract {contract_address}",
            )

        return abi_type["size"]
