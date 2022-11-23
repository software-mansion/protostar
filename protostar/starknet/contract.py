import asyncio
from typing import Optional, Tuple

from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starknet.testing.contract import StarknetContractFunctionInvocation
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.execution.objects import CallInfo
from starkware.starknet.business_logic.transaction.fee import calculate_tx_fee
from starkware.starknet.business_logic.utils import calculate_tx_resources
from starkware.starknet.business_logic.state.state import (
    UpdatesTrackerState,
    StateSyncifier,
    CachedState,
)
from starkware.starknet.definitions.transaction_type import TransactionType
from starkware.starknet.definitions.general_config import StarknetGeneralConfig

from protostar.starknet.cheatable_state import CheatableStarknetState

from .cheatable_state import CheatableStarknetState


async def execute_on_state(
    invocation: StarknetContractFunctionInvocation,
    state: CheatableStarknetState,
    caller_address: int = 0,
    resources_manager: Optional[ExecutionResourcesManager] = None,
) -> Tuple[StarknetCallInfo, CallInfo]:
    """
    Executes the function call and apply changes on the given state.
    custom version of StarknetContractFunctionInvocation._execute_on_given_state()
    """
    call_info = await state.execute_entry_point_raw(
        contract_address=invocation.contract_address,
        selector=invocation.name,
        calldata=invocation.calldata,
        caller_address=caller_address,
        resources_manager=resources_manager,
    )
    if invocation.has_raw_output:
        # Return the result as a raw tuple.
        result = tuple(call_info.retdata)
    else:
        args = invocation._build_arguments(  # pylint: disable=protected-access
            arg_values=call_info.retdata,
            arg_types=invocation.retdata_arg_types,
        )
        result = invocation.retdata_tuple(*args)

    main_call_raw_events = call_info.events

    return (
        StarknetCallInfo.from_internal(
            call_info=call_info,
            result=result,
            main_call_events=invocation._build_events(  # pylint: disable=protected-access
                raw_events=main_call_raw_events
            ),
        ),
        call_info,
    )


def estimate_fee(
    state: CachedState,
    starknet_general_config: StarknetGeneralConfig,
    resources_manager: ExecutionResourcesManager,
    call_info: CallInfo,
    l1_gas_price: int,
):
    loop = asyncio.get_running_loop()
    resources_manager = ExecutionResourcesManager.empty()
    sync_state = StateSyncifier(async_state=state, loop=loop)
    tracker_state = UpdatesTrackerState(state=sync_state)
    resources = calculate_tx_resources(
        state=tracker_state,
        resources_manager=resources_manager,
        call_infos=[call_info],
        tx_type=TransactionType.INVOKE_FUNCTION,
    )
    estimated_fee = calculate_tx_fee(
        resources,
        gas_price=l1_gas_price,
        general_config=starknet_general_config,
    )
    return estimated_fee
