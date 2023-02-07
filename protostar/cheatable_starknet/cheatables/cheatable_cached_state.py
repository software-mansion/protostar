# pylint: disable=duplicate-code
# pylint: disable=protected-access

import dataclasses
from typing import Optional

from starkware.starknet.business_logic.state.state import (
    ContractClassCache,
    CachedState,
)
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.business_logic.state.state_api import StateReader
from typing_extensions import Self

from protostar.cairo_testing.cairo_test_execution_state import (
    ContractsControllerState,
    BlockInfoControllerState,
)
from protostar.starknet.address import Address


# pylint: disable=too-many-instance-attributes
class CheatableCachedState(CachedState):
    def __init__(
        self,
        block_info: BlockInfo,
        state_reader: StateReader,
        contract_class_cache: ContractClassCache,
        contracts_controller_state: "ContractsControllerState",
        block_info_controller_state: "BlockInfoControllerState",
    ):
        super().__init__(
            block_info=block_info,
            state_reader=state_reader,
            contract_class_cache=contract_class_cache,
        )
        self._contracts_controller_state = contracts_controller_state
        self._block_info_controller_state = block_info_controller_state

    def get_pranked_address(self, target_address: Address) -> Optional[Address]:
        return self._contracts_controller_state.get_pranked_address(target_address)

    def get_block_info(self, contract_address: int) -> BlockInfo:
        block_info = self.block_info
        block_timestamp = self._block_info_controller_state.get_block_timestamp(
            Address(contract_address)
        )
        if block_timestamp is not None:
            block_info = dataclasses.replace(
                block_info,
                block_timestamp=block_timestamp,
            )
        block_number = self._block_info_controller_state.get_block_number(
            Address(contract_address)
        )
        if block_number is not None:
            block_info = dataclasses.replace(
                block_info,
                block_number=block_number,
            )
        return block_info

    def _copy(self):
        return CheatableCachedState(
            block_info=self.block_info,
            state_reader=self,
            contract_class_cache=self.contract_classes,
            contracts_controller_state=self._contracts_controller_state,
            block_info_controller_state=self._block_info_controller_state,
        )

    def _apply(self, parent: Self):
        assert isinstance(parent, self.__class__)
        super()._apply(parent)


class CheatableStateException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.message)
