from abc import ABC, abstractmethod
from typing import Optional

from starkware.starknet.testing.objects import StarknetTransactionExecutionInfo
from starkware.starkware_utils.error_handling import StarkException

from protostar.commands.test.execution_state import ExecutionState
from protostar.commands.test.starkware import ExecutionResourcesSummary
from protostar.commands.test.starkware.cheatable_execute_entry_point import (
    CheatableExecuteEntryPoint,
)
from protostar.commands.test.starkware.cheatcode_factory import CheatcodeFactory
from protostar.commands.test.test_context import TestContextHintLocal
from protostar.commands.test.test_environment_exceptions import (
    StarknetRevertableException,
)


class ExecutionEnvironment(ABC):
    def __init__(self, state: ExecutionState):
        self.state: ExecutionState = state

    @abstractmethod
    def _cheatcode_factory(self) -> CheatcodeFactory:
        ...

    async def _invoke(self, function_name: str) -> Optional[ExecutionResourcesSummary]:
        return await self._call(function_name)

    async def invoke(self, function_name: str) -> Optional[ExecutionResourcesSummary]:
        """
        Final. Override ``_invoke`` if needed.
        """
        CheatableExecuteEntryPoint.cheatcode_factory = self._cheatcode_factory()
        CheatableExecuteEntryPoint.custom_hint_locals = [
            TestContextHintLocal(self.state.context)
        ]

        return await self._invoke(function_name)

    async def _call(self, function_name: str) -> ExecutionResourcesSummary:
        try:
            func = getattr(self.state.contract, function_name)
            tx_info: StarknetTransactionExecutionInfo = await func().invoke()
            return ExecutionResourcesSummary.from_execution_resources(
                tx_info.call_info.execution_resources
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
