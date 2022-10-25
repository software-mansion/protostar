from typing import List

from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import MaxExamplesCheatcode
from protostar.testing.environments.execution_environment import ExecutionEnvironment
from protostar.testing.starkware.test_execution_state import TestExecutionState

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
    ) -> List[Cheatcode]:
        return [
            *super().build_cheatcodes(syscall_dependencies),
            MaxExamplesCheatcode(syscall_dependencies, self._state.config),
        ]
