# pylint: disable=duplicate-code
# pylint: disable=protected-access

from pathlib import Path
from typing import Dict, Optional

from starkware.starknet.business_logic.state.state import (
    ContractClassCache,
    CachedState,
)
from starkware.starknet.public.abi import AbiType
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.business_logic.state.state_api import StateReader
from typing_extensions import Self

from protostar.cheatable_starknet.controllers.expect_events_controller import Event
from protostar.starknet.address import Address
from protostar.cheatable_starknet.controllers.block_info import BlockInfoController
from protostar.starknet.selector import Selector
from protostar.starknet.types import ClassHashType
from protostar.starknet.data_transformer import CairoData
from protostar.cheatable_starknet.controllers.expect_call_controller import FunctionCall


# pylint: disable=too-many-instance-attributes
class CheatableCachedState(CachedState):
    def __init__(
        self,
        block_info: BlockInfo,
        state_reader: StateReader,
        contract_class_cache: ContractClassCache,
    ):
        super().__init__(
            block_info=block_info,
            state_reader=state_reader,
            contract_class_cache=contract_class_cache,
        )

        self._target_address_to_pranked_address: dict[Address, Address] = {}
        self.mocked_calls: dict[Address, dict[Selector, CairoData]] = {}
        self.event_selector_to_name_map: Dict[int, str] = {}
        self.emitted_events: list[Event] = []
        self.event_name_to_contract_abi_map: Dict[str, AbiType] = {}
        self.class_hash_to_contract_abi_map: Dict[ClassHashType, AbiType] = {}
        self.class_hash_to_contract_path_map: Dict[ClassHashType, Path] = {}
        self.contract_address_to_class_hash_map: Dict[Address, ClassHashType] = {}
        self.expected_contract_calls: dict[Address, list[FunctionCall]] = {}

        self.contract_address_to_block_timestamp: dict[Address, int] = {}
        self.contract_address_to_block_number: dict[Address, int] = {}

    def add_mocked_response(
        self,
        target_address: Address,
        entrypoint: Selector,
        mocked_response: CairoData,
    ) -> None:
        if target_address not in self.mocked_calls:
            self.mocked_calls[target_address] = {}
        self.mocked_calls[target_address][entrypoint] = mocked_response

    def get_mocked_response(
        self, target_address: Address, entrypoint: Selector
    ) -> Optional[CairoData]:
        return self.mocked_calls.get(target_address, {}).get(entrypoint, None)

    def get_pranked_address(self, target_address: Address) -> Optional[Address]:
        if target_address in self._target_address_to_pranked_address:
            return self._target_address_to_pranked_address[target_address]
        return None

    def set_pranked_address(self, target_address: Address, pranked_address: Address):
        self._target_address_to_pranked_address[target_address] = pranked_address

    def remove_pranked_address(self, target_address: Address):
        if target_address in self._target_address_to_pranked_address:
            del self._target_address_to_pranked_address[target_address]

    def get_block_info(self, contract_address: int) -> BlockInfo:
        return BlockInfoController(self).get_for_contract(Address(contract_address))

    def _copy(self):
        copied = CheatableCachedState(
            block_info=self.block_info,
            state_reader=self,
            contract_class_cache=self.contract_classes,
        )

        copied._target_address_to_pranked_address = (
            self._target_address_to_pranked_address.copy()
        )
        copied.mocked_calls = self.mocked_calls.copy()

        copied.event_selector_to_name_map = self.event_selector_to_name_map.copy()

        copied.event_name_to_contract_abi_map = (
            self.event_name_to_contract_abi_map.copy()
        )
        copied.class_hash_to_contract_abi_map = (
            self.class_hash_to_contract_abi_map.copy()
        )
        copied.class_hash_to_contract_path_map = (
            self.class_hash_to_contract_path_map.copy()
        )
        copied.contract_address_to_class_hash_map = (
            self.contract_address_to_class_hash_map.copy()
        )
        copied.expected_contract_calls = self.expected_contract_calls.copy()

        copied.contract_address_to_block_timestamp = (
            self.contract_address_to_block_timestamp.copy()
        )
        copied.contract_address_to_block_number = (
            self.contract_address_to_block_number.copy()
        )
        copied.emitted_events = self.emitted_events.copy()

        return copied

    def _apply(self, parent: Self):
        assert isinstance(parent, self.__class__)
        super()._apply(parent)

        parent._target_address_to_pranked_address = {
            **parent._target_address_to_pranked_address,
            **self._target_address_to_pranked_address,
        }

        parent.mocked_calls = {**parent.mocked_calls}

        # pylint: disable=consider-using-dict-items
        for address in self.mocked_calls:
            if address in parent.mocked_calls:
                parent.mocked_calls[address] = {
                    **parent.mocked_calls[address],
                    **self.mocked_calls[address],
                }
            else:
                parent.mocked_calls[address] = self.mocked_calls[address]

        parent.event_selector_to_name_map = {
            **parent.event_selector_to_name_map,
            **self.event_selector_to_name_map,
        }

        parent.event_name_to_contract_abi_map = {
            **parent.event_name_to_contract_abi_map,
            **self.event_name_to_contract_abi_map,
        }

        parent.class_hash_to_contract_path_map = {
            **parent.class_hash_to_contract_path_map,
            **self.class_hash_to_contract_path_map,
        }
        parent.class_hash_to_contract_abi_map = {
            **parent.class_hash_to_contract_abi_map,
            **self.class_hash_to_contract_abi_map,
        }
        parent.contract_address_to_class_hash_map = {
            **parent.contract_address_to_class_hash_map,
            **self.contract_address_to_class_hash_map,
        }
        parent.expected_contract_calls = {
            **parent.expected_contract_calls,
            **self.expected_contract_calls,
        }
        parent.contract_address_to_block_timestamp = {
            **parent.contract_address_to_block_timestamp,
            **self.contract_address_to_block_timestamp,
        }
        parent.contract_address_to_block_number = {
            **parent.contract_address_to_block_number,
            **self.contract_address_to_block_number,
        }
        parent.emitted_events = [
            *parent.emitted_events,
            *self.emitted_events,
        ]

    def update_event_selector_to_name_map(
        self, local_event_selector_to_name_map: Dict[int, str]
    ):
        for selector, name in local_event_selector_to_name_map.items():
            self.event_selector_to_name_map[selector] = name

    def get_abi_from_contract_address(self, contract_address: int) -> AbiType:
        if contract_address not in self.contract_address_to_class_hash_map:
            raise CheatableStateException(
                (
                    "Couldn't map the `contract_address` to the `class_hash`.\n"
                    f"Is the `contract_address` ({contract_address}) valid?\n"
                ),
            )
        class_hash = self.contract_address_to_class_hash_map[contract_address]
        if class_hash not in self.class_hash_to_contract_abi_map:
            raise CheatableStateException(
                (
                    "Couldn't map the `class_hash` to the `contract_abi`.\n"
                    f"Is the `class_hash` ({class_hash}) valid?\n"
                ),
            )

        return self.class_hash_to_contract_abi_map[class_hash]


class CheatableStateException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.message)
