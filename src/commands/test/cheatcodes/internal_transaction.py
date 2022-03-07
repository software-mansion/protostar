import asyncio
from typing import Tuple

from starkware.cairo.common.cairo_function_runner import CairoFunctionRunner
from starkware.starknet.business_logic.internal_transaction import (
    InternalInvokeFunction,
)
from starkware.starknet.business_logic.state import CarriedState
from starkware.starknet.business_logic.transaction_execution_objects import (
    TransactionExecutionContext,
)
from starkware.starknet.core.os import syscall_utils
from starkware.starknet.definitions.general_config import StarknetGeneralConfig


class CheatableInternalInvokeFunction(InternalInvokeFunction):
    def _run(
        self,
        state: CarriedState,
        general_config: StarknetGeneralConfig,
        loop: asyncio.AbstractEventLoop,
        caller_address: int,
        tx_execution_context: TransactionExecutionContext,
    ) -> Tuple[CairoFunctionRunner, syscall_utils.BusinessLogicSysCallHandler]:
        raise BaseException("test")
