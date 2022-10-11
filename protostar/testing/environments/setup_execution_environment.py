from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import MaxExamplesCheatcode
from protostar.testing.environments.execution_environment import (
    ExecutionEnvironment,
)
from protostar.testing.starkware.test_execution_state import TestExecutionState

from .common_test_cheatcode_factory import CommonTestCheatcodeFactory
from ...compiler import ProjectCompiler


class SetupExecutionEnvironment(ExecutionEnvironment[None]):
    state: TestExecutionState

    def __init__(self, state: TestExecutionState, project_compiler: ProjectCompiler):
        super().__init__(state)
        self._project_compiler = project_compiler

    async def execute(self, function_name: str):
        self.set_cheatcodes(SetupCheatcodeFactory(self.state, self._project_compiler))

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
