# pylint: disable=duplicate-code
# pylint: disable=protected-access

import dataclasses
from typing import TYPE_CHECKING, Optional

from starkware.starknet.business_logic.state.state import (
    ContractClassCache,
    CachedState,
)
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.business_logic.state.state_api import StateReader

from protostar.starknet.address import Address

if TYPE_CHECKING:
    from protostar.cairo_testing.cairo_test_execution_state import (
        ContractsControllerState,
        BlockInfoControllerState,
    )


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
        self.contracts_controller_state = contracts_controller_state
        self.block_info_controller_state = block_info_controller_state

    def get_pranked_address(self, target_address: Address) -> Optional[Address]:
        return self.contracts_controller_state.get_pranked_address(target_address)

    def get_block_info(self, contract_address: int) -> BlockInfo:
        block_info = self.block_info
        block_timestamp = self.block_info_controller_state.get_block_timestamp(
            Address(contract_address)
        )
        if block_timestamp is not None:
            block_info = dataclasses.replace(
                block_info,
                block_timestamp=block_timestamp,
            )
        block_number = self.block_info_controller_state.get_block_number(
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
            contracts_controller_state=self.contracts_controller_state,
            block_info_controller_state=self.block_info_controller_state,
        )

    def _apply(self, parent: "CachedState"):
        assert isinstance(parent, self.__class__)
        parent.block_info_controller_state = self.block_info_controller_state
        parent.contracts_controller_state = self.contracts_controller_state
        return super()._apply(parent)


class CheatableStateException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.message)
