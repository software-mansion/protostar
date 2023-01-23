from typing import List

from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import MaxExamplesCheatcode
from .common_test_cheatcode_factory import CommonTestCheatcodeFactory
from .contract_based_test_execution_environment import (
    ContractBasedTestExecutionEnvironment,
)


class SetupExecutionEnvironment(ContractBasedTestExecutionEnvironment):
    async def execute(self, function_name: str) -> None:
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
