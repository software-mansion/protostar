from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starkware_utils.error_handling import StarkException

from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet.execution_state import ExecutionState
from protostar.testing.test_environment_exceptions import (
    StarknetRevertableException,
)

InvokeResultT = TypeVar("InvokeResultT")


class ExecutionEnvironment(ABC, Generic[InvokeResultT]):
    def __init__(self, state: ExecutionState):
        self.state: ExecutionState = state

    @abstractmethod
    async def execute(self, function_name: str) -> InvokeResultT:
        ...

    async def perform_execute(
        self, function_name: str, *args, **kwargs
    ) -> StarknetCallInfo:
        try:
            func = getattr(self.state.contract, function_name)
            return await func(*args, **kwargs).execute()
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
