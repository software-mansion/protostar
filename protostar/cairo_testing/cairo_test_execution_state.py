import dataclasses
from copy import deepcopy
from dataclasses import dataclass, field
from typing import cast

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
from protostar.testing.stopwatch import Stopwatch
from protostar.testing.test_config import TestConfig
from protostar.testing.test_context import TestContext
from protostar.testing.test_output_recorder import OutputRecorder


@dataclass
class CairoTestExecutionState:
    starknet: Starknet
    stopwatch: Stopwatch
    output_recorder: OutputRecorder
    context: TestContext
    config: TestConfig
    project_compiler: ProjectCompiler
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
        )
