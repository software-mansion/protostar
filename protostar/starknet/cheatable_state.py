from typing import List, Optional, Union, cast

from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionInfo,
    CallInfo,
)
from starkware.starknet.business_logic.fact_state.patricia_state import (
    PatriciaStateReader,
)
from starkware.starknet.business_logic.fact_state.state import (
    SharedState,
)
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starknet.definitions import constants
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class import EntryPointType
from starkware.starknet.testing.state import StarknetState, CastableToAddress
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext

from protostar.starknet.cheatable_cached_state import CheatableCachedState
from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
from protostar.starknet.cheatable_invoke_function import (
    create_cheatable_invoke_function,
)


class CheatableStarknetState(StarknetState):
    def __init__(
        self,
        state: CheatableCachedState,
        general_config: StarknetGeneralConfig,
    ):
        super().__init__(state, general_config)

    @property
    def cheatable_state(self) -> CheatableCachedState:
        return cast(CheatableCachedState, self.state)

    async def invoke_raw(
        self,
        contract_address: CastableToAddress,
        selector: Union[int, str],
        calldata: List[int],
        max_fee: int,
        signature: Optional[List[int]] = None,
        nonce: Optional[int] = None,
    ) -> TransactionExecutionInfo:
        # region Modified Starknet code.
        tx = await create_cheatable_invoke_function(
            state=self.cheatable_state,
            contract_address=contract_address,
            selector=selector,
            calldata=calldata,
            max_fee=max_fee,
            version=constants.TRANSACTION_VERSION,
            signature=signature,
            nonce=nonce,
            chain_id=self.general_config.chain_id.value,
        )
        # endregion
        return await self.execute_tx(tx=tx)

    async def execute_entry_point_raw(
        self,
        contract_address: CastableToAddress,
        selector: Union[int, str],
        calldata: List[int],
        caller_address: int,
    ) -> CallInfo:
        if isinstance(contract_address, str):
            contract_address = int(contract_address, 16)
        assert isinstance(contract_address, int)

        # region Modified Starknet code.
        if isinstance(selector, str):
            numeric_selector = get_selector_from_name(selector)
            if isinstance(self.state, CheatableCachedState):
                self.cheatable_state.entry_points_selectors_to_names[
                    numeric_selector
                ] = selector
            selector = numeric_selector
        assert isinstance(selector, int)

        call = CheatableExecuteEntryPoint.create(
            contract_address=contract_address,
            entry_point_selector=selector,
            entry_point_type=EntryPointType.EXTERNAL,
            calldata=calldata,
            caller_address=caller_address,
        )

        with self.state.copy_and_apply() as state_copy:
            if all(
                isinstance(item, CheatableCachedState)
                for item in [self.state, state_copy]
            ):
                state_copy.entry_points_selectors_to_names = self.state.entry_points_selectors_to_names  # type: ignore
            call_info = await call.execute_for_testing(
                state=state_copy,
                general_config=self.general_config,
            )
        # endregion

        self.add_messages_and_events(execution_info=call_info)

        return call_info

    @classmethod
    async def empty(
        cls, general_config: Optional[StarknetGeneralConfig] = None
    ) -> "CheatableStarknetState":
        if general_config is None:
            general_config = StarknetGeneralConfig()

        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)
        empty_shared_state = await SharedState.empty(
            ffc=ffc, general_config=general_config
        )
        state_reader = PatriciaStateReader(
            global_state_root=empty_shared_state.contract_states, ffc=ffc
        )
        # region Modified Starknet code.
        state = CheatableCachedState(
            block_info=BlockInfo.empty(
                sequencer_address=general_config.sequencer_address
            ),
            state_reader=state_reader,
        )
        # endregion

        return cls(state=state, general_config=general_config)

    def copy(self) -> "CheatableStarknetState":
        return cast(CheatableStarknetState, super().copy())
