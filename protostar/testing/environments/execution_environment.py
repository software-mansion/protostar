from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Optional

from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.contract import StarknetContractFunctionInvocation
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.testing.test_environment_exceptions import StarknetRevertableException
from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet import execute_on_state, ExecutionState

InvokeResultT = TypeVar("InvokeResultT")


@dataclass
class PerformExecuteResult:
    starknet_call_info: StarknetCallInfo
    call_info: CallInfo
    resources_manager: ExecutionResourcesManager


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
    ) -> PerformExecuteResult:
        try:
            func = self.state.contract.get_contract_function(function_name)
            invocation: StarknetContractFunctionInvocation = func(*args, **kwargs)
            resources_manager = ExecutionResourcesManager.empty()
            starknet_call_info, call_info = await execute_on_state(
                invocation,
                self.state.starknet.cheatable_state,
                resources_manager=resources_manager,
            )
            return PerformExecuteResult(
                call_info=call_info,
                resources_manager=resources_manager,
                starknet_call_info=starknet_call_info,
            )
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
