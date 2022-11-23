from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Optional

from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.contract import StarknetContractFunctionInvocation
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager

from protostar.testing.test_environment_exceptions import StarknetRevertableException
from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet import estimate_fee as estimate_fee_from_resources_manager
from protostar.starknet import execute_on_state, ExecutionState

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
        estimate_fee: bool = False,
        **kwargs: Any,
    ) -> tuple[StarknetCallInfo, Optional[int]]:
        try:
            func = getattr(self.state.contract, function_name)
            if not estimate_fee:
                return await func(*args, **kwargs).execute(), None
            resources_manager = ExecutionResourcesManager.empty()
            invocation: StarknetContractFunctionInvocation = func(*args, **kwargs)
            result, call_info = await execute_on_state(
                invocation,
                self.state.starknet.cheatable_state,
                resources_manager=resources_manager,
            )
            estimated_fee = estimate_fee_from_resources_manager(
                state=self.state.starknet.state.state,
                call_info=call_info,
                resources_manager=resources_manager,
                starknet_general_config=self.state.starknet.state.general_config,
            )
            return result, estimated_fee
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

    @staticmethod
    def set_max_steps(value: Optional[int]):
        CheatableExecuteEntryPoint.max_steps = value
