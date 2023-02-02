import dataclasses
from typing import TYPE_CHECKING

from starkware.starknet.business_logic.state.state_api_objects import BlockInfo

from protostar.starknet.address import Address

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


class BlockInfoController:
    def __init__(self, cheatable_state: "CheatableCachedState"):
        self.cheatable_state = cheatable_state

    def get_for_contract(self, contract_address: Address) -> BlockInfo:
        block_info = self.cheatable_state.block_info

        block_timestamp = self.cheatable_state.contract_address_to_block_timestamp.get(
            contract_address
        )
        if block_timestamp is not None:
            block_info = dataclasses.replace(
                block_info,
                block_timestamp=block_timestamp,
            )

        block_number = self.cheatable_state.contract_address_to_block_number.get(
            contract_address
        )
        if block_number is not None:
            block_info = dataclasses.replace(
                block_info,
                block_number=block_number,
            )

        return block_info

    def set_block_timestamp(
        self,
        contract_address: Address,
        block_timestamp: int,
    ):
        self.cheatable_state.contract_address_to_block_timestamp[
            contract_address
        ] = block_timestamp

    def set_block_number(self, contract_address: Address, block_number: int):
        self.cheatable_state.contract_address_to_block_number[
            contract_address
        ] = block_number

    def clear_block_number_cheat(self, contract_address: Address):
        del self.cheatable_state.contract_address_to_block_number[contract_address]

    def clear_block_timestamp_cheat(self, contract_address: Address):
        del self.cheatable_state.contract_address_to_block_timestamp[contract_address]
