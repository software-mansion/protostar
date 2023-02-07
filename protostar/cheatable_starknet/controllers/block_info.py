from typing import TYPE_CHECKING

from protostar.starknet.address import Address

if TYPE_CHECKING:
    from protostar.cairo_testing.cairo_test_execution_state import (
        BlockInfoControllerState,
    )
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


class BlockInfoController:
    def __init__(
        self, state: "BlockInfoControllerState", cheatable_state: "CheatableCachedState"
    ):
        self._state = state
        self._cheatable_state = cheatable_state

    def set_block_timestamp(
        self,
        contract_address: Address,
        block_timestamp: int,
    ):
        self._state.set_block_timestamp(
            contract_address=contract_address, block_timestamp=block_timestamp
        )

    def set_block_number(self, contract_address: Address, block_number: int):
        self._state.set_block_number(
            contract_address=contract_address, block_number=block_number
        )

    def clear_block_number_cheat(self, contract_address: Address):
        self._state.remove_block_number(contract_address)

    def clear_block_timestamp_cheat(self, contract_address: Address):
        self._state.remove_block_timestamp(contract_address)
