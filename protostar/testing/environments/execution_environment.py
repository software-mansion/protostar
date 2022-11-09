from abc import ABC, abstractmethod
import asyncio
from typing import Generic, Optional, Tuple, TypeVar, Any

from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starknet.services.api.feeder_gateway.response_objects import FunctionInvocation
from starkware.starkware_utils.error_handling import StarkException

from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
from protostar.starknet.cheatable_state import CheatableStarknetState
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet.execution_state import ExecutionState
from starkware.starknet.testing.contract import StarknetContractFunctionInvocation
from starkware.starknet.business_logic.transaction.fee import calculate_tx_fee
from protostar.testing.test_environment_exceptions import (
    StarknetRevertableException,
)
from starkware.starknet.business_logic.utils import (
    calculate_tx_resources,
)
from starkware.starknet.business_logic.state.state import UpdatesTrackerState
from starkware.starknet.business_logic.state.state import StateSyncifier
from starkware.starknet.definitions.transaction_type import TransactionType
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.execution.objects import (CallInfo, OrderedL2ToL1Message)
from starkware.python.utils import to_bytes
from starkware.starknet.services.api.feeder_gateway.response_objects import (
    TransactionTrace,
)
from starknet_devnet.util import get_fee_estimation_info

InvokeResultT = TypeVar("InvokeResultT")


class ExecutionEnvironment(ABC, Generic[InvokeResultT]):
    def __init__(self, state: ExecutionState):
        self.state: ExecutionState = state

    @abstractmethod
    async def execute(self, function_name: str) -> InvokeResultT:
        ...

    async def perform_execute(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> StarknetCallInfo:
        try:
            resources_manager = ExecutionResourcesManager.empty()
            func = getattr(self.state.contract, function_name)
            invoc: StarknetContractFunctionInvocation = func(*args, **kwargs)
            result, call_info = await execute_on_state(invoc, self.state.starknet.cheatable_state, resources_manager=resources_manager) 
            loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
            sync_state = StateSyncifier(async_state=self.state.starknet.state.state, loop=loop)
            tracker_state = UpdatesTrackerState(state=sync_state)
            actual_resources = calculate_tx_resources(
                state=tracker_state,
                resources_manager=resources_manager,
                call_infos=[call_info],
                tx_type=TransactionType.INVOKE_FUNCTION,
            )
            # sync_state.block_info.gas_price is 0 :(
            # We can just show estimated gas instead of fee?
            actual_fee = calculate_tx_fee(
                actual_resources,
                1,
                self.state.starknet.state.general_config,
            )

            print(sync_state.block_info.gas_price)
            print(actual_resources)
            print(actual_fee)
            return result

        except StarkException as ex:
            raise StarknetRevertableException(
                error_message=StarknetRevertableException.extract_error_messages_from_stark_ex_message(
                    ex.message
                ),
                error_type=ex.code.name,
                code=ex.code.value,
                details=ex.message,
            ) from ex

    # TODO(mkaput): Replace these two with stateless parameters passing to ForkableStarknet.
    @staticmethod
    def set_cheatcodes(cheatcode_factory: CheatcodeFactory):
        CheatableExecuteEntryPoint.cheatcode_factory = cheatcode_factory

    @staticmethod
    def set_profile_flag(value: bool):
        CheatableExecuteEntryPoint.profiling = value

async def execute_on_state(
        invocation: StarknetContractFunctionInvocation,
        state: CheatableStarknetState,
        caller_address: int = 0,
        resources_manager: Optional[ExecutionResourcesManager] = None,
    ) -> Tuple[StarknetCallInfo, CallInfo]:
        """
        Executes the function call and apply changes on the given state.
        """
        call_info = await state.execute_entry_point_raw(
            contract_address=invocation.contract_address,
            selector=invocation.name,
            calldata=invocation.calldata,
            caller_address=caller_address,
            resources_manager=resources_manager
        )
        if invocation.has_raw_output:
            # Return the result as a raw tuple.
            result = tuple(call_info.retdata)
        else:
            args = invocation._build_arguments(
                arg_values=call_info.retdata,
                arg_types=invocation.retdata_arg_types,
            )
            result = invocation.retdata_tuple(*args)

        main_call_raw_events = call_info.events

        return StarknetCallInfo.from_internal(
            call_info=call_info,
            result=result,
            main_call_events=invocation._build_events(raw_events=main_call_raw_events),
        ), call_info
