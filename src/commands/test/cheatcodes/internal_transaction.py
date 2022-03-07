import asyncio

from starkware.starknet.business_logic.internal_transaction import (
    InternalInvokeFunction,
)
from starkware.starknet.business_logic.state import CarriedState
from starkware.starknet.business_logic.transaction_execution_objects import (
    TransactionExecutionContext,
    TransactionExecutionInfo,
)
from starkware.starknet.definitions.general_config import StarknetGeneralConfig


class CheatableInternalInvokeFunction(InternalInvokeFunction):
    def _synchronous_apply_specific_state_updates(
        self,
        state: CarriedState,
        general_config: StarknetGeneralConfig,
        loop: asyncio.AbstractEventLoop,
        tx_execution_context: TransactionExecutionContext,
    ) -> TransactionExecutionInfo:
        raise NotImplementedError
