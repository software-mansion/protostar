import dataclasses
from copy import copy
from typing import Optional, Callable

from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from typing_extensions import Self

from protostar.starknet.cheater import Cheater
from protostar.starknet.types import AddressType


class BlockInfoCheater(Cheater):
    def __init__(self, base: BlockInfo):
        self.base: BlockInfo = base

        self._contract_address_to_block_timestamp: dict[AddressType, int] = {}
        self._contract_address_to_block_number: dict[AddressType, int] = {}

    def get_for_contract(self, contract_address: AddressType) -> BlockInfo:
        block_info = self.base

        block_timestamp = self._contract_address_to_block_timestamp.get(
            contract_address
        )
        if block_timestamp is not None:
            block_info = dataclasses.replace(
                block_info,
                block_timestamp=block_timestamp,
            )

        block_number = self._contract_address_to_block_number.get(contract_address)
        if block_number is not None:
            block_info = dataclasses.replace(
                block_info,
                block_number=block_number,
            )

        return block_info

    def cheat(
        self,
        contract_address: AddressType,
        block_timestamp: Optional[int] = None,
        block_number: Optional[int] = None,
    ) -> Callable[[], None]:
        if block_timestamp is not None:
            self._contract_address_to_block_timestamp[
                contract_address
            ] = block_timestamp

        if block_number is not None:
            self._contract_address_to_block_number[contract_address] = block_number

        def stop() -> None:
            if block_timestamp is not None:
                del self._contract_address_to_block_timestamp[contract_address]

            if block_number is not None:
                del self._contract_address_to_block_number[contract_address]

        return stop

    def copy(self) -> Self:
        return copy(self)

    def apply(self, parent: Self) -> None:
        parent._contract_address_to_block_timestamp = {
            **parent._contract_address_to_block_timestamp,
            **self._contract_address_to_block_timestamp,
        }

        parent._contract_address_to_block_number = {
            **parent._contract_address_to_block_number,
            **self._contract_address_to_block_number,
        }
