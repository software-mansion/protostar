import dataclasses
from typing import Optional, Callable, TYPE_CHECKING

from starkware.starknet.business_logic.state.state_api_objects import BlockInfo

from protostar.starknet.address import Address

if TYPE_CHECKING:
    from protostar.cheatable_starknet.cheatables import CheatableCachedState


class BlockInfoCairoCheater:
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

    def cheat(
        self,
        contract_address: Address,
        block_timestamp: Optional[int] = None,
        block_number: Optional[int] = None,
    ) -> Callable[[], None]:
        if block_timestamp is not None:
            self.cheatable_state.contract_address_to_block_timestamp[
                contract_address
            ] = block_timestamp

        if block_number is not None:
            self.cheatable_state.contract_address_to_block_number[
                contract_address
            ] = block_number

        def stop() -> None:
            if block_timestamp is not None:
                del self.cheatable_state.contract_address_to_block_timestamp[
                    contract_address
                ]

            if block_number is not None:
                del self.cheatable_state.contract_address_to_block_number[
                    contract_address
                ]

        return stop
