import copy
from typing import cast

from starkware.starknet.testing.starknet import Starknet
from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash_func
from starkware.starknet.business_logic.fact_state.patricia_state import (
    PatriciaStateReader,
)
from starkware.starknet.business_logic.fact_state.state import SharedState
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.testing.state import StarknetState
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext
from starkware.starknet.public.abi import get_selector_from_name

from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.cheatables.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.starknet import Address, CairoData


class CheatableStarknetFacade:
    @classmethod
    async def create(cls):
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
        )

    def __init__(self, starknet: Starknet) -> None:
        self._starknet = starknet

    @property
    def cheatable_state(self) -> CheatableCachedState:
        return cast(CheatableCachedState, self._starknet.state.state)

    def fork(self):
        return CheatableStarknetFacade(self._starknet)

    async def invoke(
        self, contract_address: Address, function_name: str, calldata: CairoData
    ):
        entry_point = CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=contract_address,
            calldata=calldata,
            entry_point_selector=get_selector_from_name(function_name),
        )
        with self.cheatable_state.copy_and_apply() as state_copy:
            await entry_point.execute_for_testing(
                state=state_copy,
                general_config=StarknetGeneralConfig(),
            )

    async def call(
        self, contract_address: Address, function_name: str, calldata: CairoData
    ) -> CairoData:
        entry_point = CheatableExecuteEntryPoint.create_for_protostar(
            contract_address=contract_address,
            calldata=calldata,
            entry_point_selector=get_selector_from_name(function_name),
        )
        result = await entry_point.execute_for_testing(
            state=copy.deepcopy(self.cheatable_state),
            general_config=StarknetGeneralConfig(),
        )
        return result.calldata
