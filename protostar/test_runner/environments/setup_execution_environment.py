from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.test_runner.cheatcodes import MaxExamplesCheatcode
from protostar.test_runner.starkware.test_execution_state import TestExecutionState

from .common_test_cheatcode_factory import CommonTestCheatcodeFactory


class SetupExecutionEnvironment(ExecutionEnvironment[None]):
    state: TestExecutionState

    def __init__(self, state: TestExecutionState):
        super().__init__(state)

    async def execute(self, function_name: str):
        self.set_cheatcodes(SetupCheatcodeFactory(self.state))

        with self.state.output_recorder.redirect("setup"):
            await self.perform_execute(function_name)


class SetupCheatcodeFactory(CommonTestCheatcodeFactory):
    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        return [
            *super().build_cheatcodes(syscall_dependencies, internal_calls),
            MaxExamplesCheatcode(syscall_dependencies, self._state.config),
        ]
