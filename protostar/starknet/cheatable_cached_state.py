from pathlib import Path
from typing import Dict, List, Any

from services.everest.business_logic.state_api import StateProxy
from starkware.starknet.business_logic.fact_state.state import CarriedState
from starkware.starknet.business_logic.state.state import CachedState, StateSyncifier
from starkware.starknet.public.abi import AbiType
from typing_extensions import Self

from protostar.starknet.cheaters import BlockInfoCheater, Cheaters
from protostar.starknet.types import ClassHashType, SelectorType
from protostar.starknet.data_transformer import CairoOrPythonData

from .address import Address


# pylint: disable=too-many-instance-attributes
class CheatableCachedState(CachedState):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.pranked_contracts_map: Dict[int, int] = {}
        self.mocked_calls_map: Dict[Address, Dict[SelectorType, List[int]]] = {}
        self.event_selector_to_name_map: Dict[int, str] = {}

        self.event_name_to_contract_abi_map: Dict[str, AbiType] = {}
        self.class_hash_to_contract_abi_map: Dict[ClassHashType, AbiType] = {}
        self.class_hash_to_contract_path_map: Dict[ClassHashType, Path] = {}
        self.contract_address_to_class_hash_map: Dict[Address, ClassHashType] = {}
        self.entry_points_selectors_to_names: Dict[SelectorType, str] = {}
        self.contract_calls: dict[
            Address, list[tuple[SelectorType, CairoOrPythonData]]
        ] = {}

        self.cheaters = Cheaters(block_info=BlockInfoCheater(self.block_info))

    def _copy(self):
        copied = CheatableCachedState(block_info=self.block_info, state_reader=self)

        copied.pranked_contracts_map = self.pranked_contracts_map.copy()
        copied.mocked_calls_map = self.mocked_calls_map.copy()
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
        copied.contract_calls = self.contract_calls.copy()

        copied.cheaters = self.cheaters.copy()

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
        parent.contract_calls = {
            **parent.contract_calls,
            **self.contract_calls,
        }

        parent.cheaters.apply(self.cheaters)

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


def cheaters_of(state: StateProxy) -> Cheaters:
    """
    Extracts the ``Cheaters`` object from any State structures.

    This function workarounds limitations of the inheritance design of ``State`` classes family,
    preventing us from exposing the `cheaters` field via state interface classes like ``SyncState``.
    """

    if isinstance(state, CheatableCachedState):
        return state.cheaters

    if isinstance(state, CachedState):
        raise TypeError(
            f"Protostar should always operate on {CheatableCachedState.__name__}."
        )

    if isinstance(state, CarriedState):
        state = state.state

        if not isinstance(state, CheatableCachedState):
            raise TypeError(
                f"Carried state is not carrying {CheatableCachedState.__name__}."
            )

        return state.cheaters

    if isinstance(state, StateSyncifier):
        state = state.async_state

        if not isinstance(state, CheatableCachedState):
            raise TypeError(
                f"State syncifier is not carrying {CheatableCachedState.__name__}."
            )

        return state.cheaters

    raise TypeError(f"Unknown State class {state.__class__.__name__}.")


class CheatableStateException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.message)
