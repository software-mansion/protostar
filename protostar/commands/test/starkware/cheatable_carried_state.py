from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from starkware.starknet.business_logic.state.state import CarriedState

from protostar.commands.test.starkware.types import AddressType, SelectorType


class CheatableCarriedState(CarriedState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pranked_contracts_map: Dict[int, int] = {}
        self.mocked_calls_map: Dict[
            AddressType, Dict[SelectorType, List[int]]
        ] = defaultdict(dict)
        self.contract_address_to_class_hash_map: Dict[int, int] = {}
        self.class_hash_to_contract_path_map: Dict[int, Path] = {}
        self.contract_address_to_contract_path_map: Dict[int, Path] = {}
        self.event_selector_to_name_map: Dict[int, str] = {}

    def update_event_selector_to_name_map(
        self, local_event_selector_to_name_map: Dict[int, str]
    ):
        for selector, name in local_event_selector_to_name_map.items():
            self.event_selector_to_name_map[selector] = name
