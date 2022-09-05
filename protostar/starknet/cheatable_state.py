from typing import List, Optional, Union, cast

from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.execution.objects import (
    TransactionExecutionInfo,
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
from starkware.starknet.testing.state import StarknetState, CastableToAddress
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext

from protostar.starknet.cheatable_cached_state import CheatableCachedState
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
        return await self.execute_tx(tx=tx)

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
        state = CheatableCachedState(
            block_info=BlockInfo.empty(
                sequencer_address=general_config.sequencer_address
            ),
            state_reader=state_reader,
        )

        return cls(state=state, general_config=general_config)

    def copy(self) -> "CheatableStarknetState":
        return cast(CheatableStarknetState, super().copy())
