import dataclasses
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional, cast

from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash_func
from starkware.starknet.business_logic.fact_state.patricia_state import (
    PatriciaStateReader,
)
from starkware.starknet.business_logic.fact_state.state import SharedState
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.testing.state import StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext
from typing_extensions import Self

from protostar.cheatable_starknet.controllers.expect_events_controller import Event
from protostar.compiler import ProjectCompiler
from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.starknet.address import Address
from protostar.starknet.selector import Selector
from protostar.starknet.types import ClassHashType
from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_config import TestConfig
from protostar.testing.test_context import TestContext
from protostar.testing.test_output_recorder import OutputRecorder
from protostar.starknet.abi import AbiType


class ContractsControllerState:
    def __init__(
        self,
        emitted_events: Optional[list[Event]] = None,
        class_hash_to_contract_abi: Optional[dict[ClassHashType, AbiType]] = None,
        event_selector_to_event_abi: Optional[dict[Selector, AbiType]] = None,
        address_to_class_hash: Optional[dict[Address, ClassHashType]] = None,
        target_address_to_pranked_address: Optional[dict[Address, Address]] = None,
    ) -> None:
        self._emitted_events = emitted_events or []
        self._class_hash_to_contract_abi = class_hash_to_contract_abi or {}
        self._event_selector_to_event_abi = event_selector_to_event_abi or {}
        self._contract_address_to_class_hash = address_to_class_hash or {}
        self._target_address_to_pranked_address = (
            target_address_to_pranked_address or {}
        )

    def get_emitted_events(self) -> list[Event]:
        return self._emitted_events

    def get_pranked_address(self, target_address: Address) -> Optional[Address]:
        if target_address in self._target_address_to_pranked_address:
            return self._target_address_to_pranked_address[target_address]
        return None

    def get_class_hash_from_address(self, contract_address: Address) -> ClassHashType:
        return self._contract_address_to_class_hash[contract_address]

    def get_contract_abi_from_class_hash(self, class_hash: ClassHashType) -> AbiType:
        return self._class_hash_to_contract_abi[class_hash]

    def get_contract_abi_from_contract_address(
        self, contract_address: Address
    ) -> AbiType:
        class_hash = self._contract_address_to_class_hash[contract_address]
        return self._class_hash_to_contract_abi[class_hash]

    def bind_contract_address_to_class_hash(
        self, address: Address, class_hash: ClassHashType
    ) -> None:
        self._contract_address_to_class_hash[address] = class_hash

    def bind_class_hash_to_contract_abi(
        self, class_hash: ClassHashType, contract_abi: AbiType
    ) -> None:
        self._class_hash_to_contract_abi[class_hash] = contract_abi

    def bind_event_selector_to_event_abi(
        self, event_selector: Selector, event_abi: AbiType
    ) -> None:
        self._event_selector_to_event_abi[event_selector] = event_abi

    def add_emitted_events(self, emitted_events: list[Event]) -> None:
        self._emitted_events.extend(emitted_events)

    def set_pranked_address(self, target_address: Address, pranked_address: Address):
        self._target_address_to_pranked_address[target_address] = pranked_address

    def remove_pranked_address(self, target_address: Address):
        if target_address in self._target_address_to_pranked_address:
            del self._target_address_to_pranked_address[target_address]

    def clone(self):
        return ContractsControllerState(
            emitted_events=self._emitted_events.copy(),
            class_hash_to_contract_abi=self._class_hash_to_contract_abi.copy(),
            event_selector_to_event_abi=self._event_selector_to_event_abi.copy(),
            address_to_class_hash=self._contract_address_to_class_hash.copy(),
            target_address_to_pranked_address=self._target_address_to_pranked_address.copy(),
        )


@dataclass
class CairoTestExecutionState:
    starknet: Starknet
    stopwatch: Stopwatch
    output_recorder: OutputRecorder
    context: TestContext
    config: TestConfig
    project_compiler: ProjectCompiler
    contract_controller_state: ContractsControllerState
    expected_events_list: list[list[Event]] = field(default_factory=list)

    @property
    def cheatable_state(self) -> CheatableCachedState:
        return cast(CheatableCachedState, self.starknet.state.state)

    def fork(self) -> Self:
        return dataclasses.replace(
            self,
            context=deepcopy(self.context),
            config=deepcopy(self.config),
            output_recorder=self.output_recorder.fork(),
            stopwatch=self.stopwatch.fork(),
            starknet=self.starknet.copy(),
            contract_controller_state=self.contract_controller_state.clone(),
            expected_events_list=self.expected_events_list.copy(),
        )

    @classmethod
    async def from_test_config(
        cls, test_config: TestConfig, project_compiler: ProjectCompiler
    ):
        general_config = StarknetGeneralConfig()
        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)
        empty_shared_state = await SharedState.empty(
            ffc=ffc, general_config=general_config
        )

        state_reader = PatriciaStateReader(
            global_state_root=empty_shared_state.contract_states,
            ffc=ffc,
            contract_class_storage=ffc.storage,
        )

        return cls(
            starknet=Starknet(
                state=StarknetState(
                    general_config=general_config,
                    state=CheatableCachedState(
                        block_info=BlockInfo.empty(
                            sequencer_address=general_config.sequencer_address
                        ),
                        state_reader=state_reader,
                        contract_class_cache={},
                    ),
                )
            ),
            stopwatch=Stopwatch(),
            output_recorder=OutputRecorder(),
            context=TestContext(),
            config=test_config,
            project_compiler=project_compiler,
            contract_controller_state=ContractsControllerState(),
        )
