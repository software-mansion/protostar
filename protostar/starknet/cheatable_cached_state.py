import dataclasses
from typing import Dict, List, Callable, Optional, Any

from starkware.starknet.business_logic.state.state import CachedState
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.public.abi import AbiType
from typing_extensions import Self

from protostar.commands.test.test_environment_exceptions import SimpleReportedException
from protostar.starknet.types import AddressType, SelectorType, ClassHashType


# pylint: disable=too-many-instance-attributes
class CheatableCachedState(CachedState):
    def __init__(self, *args, **kwargs):
        # Hack: Super constructor will populate this.
        self._real_block_info: Optional[BlockInfo] = None
        self._block_info_cheats: dict[str, Any] = {}

        super().__init__(*args, **kwargs)

        self.pranked_contracts_map: Dict[int, int] = {}
        self.mocked_calls_map: Dict[AddressType, Dict[SelectorType, List[int]]] = {}
        self.event_selector_to_name_map: Dict[int, str] = {}

        self.event_name_to_contract_abi_map: Dict[str, AbiType] = {}
        self.class_hash_to_contract_abi_map: Dict[ClassHashType, AbiType] = {}
        self.contract_address_to_class_hash_map: Dict[AddressType, ClassHashType] = {}

    @property
    def block_info(self) -> BlockInfo:
        return dataclasses.replace(self._real_block_info, **self._block_info_cheats)

    @block_info.setter
    def block_info(self, block_info: BlockInfo):
        self._real_block_info = block_info

    def cheat_block_info(self, **kwargs: Any) -> Callable[[], None]:
        self._block_info_cheats |= kwargs

        def stop():
            for key in kwargs.keys():
                del self._block_info_cheats[key]

        return stop

    def _copy(self):
        copied = self.__class__(block_info=self.block_info, state_reader=self)

        copied.pranked_contracts_map = self.pranked_contracts_map.copy()
        copied.mocked_calls_map = self.mocked_calls_map.copy()
        copied.event_selector_to_name_map = self.event_selector_to_name_map.copy()

        copied.event_name_to_contract_abi_map = (
            self.event_name_to_contract_abi_map.copy()
        )
        copied.class_hash_to_contract_abi_map = (
            self.class_hash_to_contract_abi_map.copy()
        )
        copied.contract_address_to_class_hash_map = (
            self.contract_address_to_class_hash_map.copy()
        )

        return copied

    def _apply(self, parent: Self):
        assert isinstance(parent, self.__class__)
        super()._apply(parent)

        parent.pranked_contracts_map = {
            **parent.pranked_contracts_map,
            **self.pranked_contracts_map,
        }

        parent.mocked_calls_map = {**parent.mocked_calls_map}

        # pylint: disable=consider-using-dict-items
        for address in self.mocked_calls_map:
            if address in parent.mocked_calls_map:
                parent.mocked_calls_map[address] = {
                    **parent.mocked_calls_map[address],
                    **self.mocked_calls_map[address],
                }
            else:
                parent.mocked_calls_map[address] = self.mocked_calls_map[address]

        parent.event_selector_to_name_map = {
            **parent.event_selector_to_name_map,
            **self.event_selector_to_name_map,
        }

        parent.event_name_to_contract_abi_map = {
            **parent.event_name_to_contract_abi_map,
            **self.event_name_to_contract_abi_map,
        }

        parent.class_hash_to_contract_abi_map = {
            **parent.class_hash_to_contract_abi_map,
            **self.class_hash_to_contract_abi_map,
        }
        parent.contract_address_to_class_hash_map = {
            **parent.contract_address_to_class_hash_map,
            **self.contract_address_to_class_hash_map,
        }

    def update_event_selector_to_name_map(
        self, local_event_selector_to_name_map: Dict[int, str]
    ):
        for selector, name in local_event_selector_to_name_map.items():
            self.event_selector_to_name_map[selector] = name

    def get_abi_from_contract_address(self, contract_address: int) -> AbiType:
        if contract_address not in self.contract_address_to_class_hash_map:
            raise SimpleReportedException(
                (
                    "Couldn't map the `contract_address` to the `class_hash`.\n"
                    f"Is the `contract_address` ({contract_address}) valid?\n"
                ),
            )
        class_hash = self.contract_address_to_class_hash_map[contract_address]
        if class_hash not in self.class_hash_to_contract_abi_map:
            raise SimpleReportedException(
                (
                    "Couldn't map the `class_hash` to the `contract_abi`.\n"
                    f"Is the `class_hash` ({class_hash}) valid?\n"
                ),
            )

        return self.class_hash_to_contract_abi_map[class_hash]
