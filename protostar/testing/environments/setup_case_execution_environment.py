from typing import List

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.hint_local import HintLocal
from protostar.testing.cheatcodes import ExampleCheatcode, GivenCheatcode, SkipCheatcode
from protostar.testing.fuzzing.strategies import StrategiesHintLocal

from .setup_execution_environment import (
    SetupCheatcodeFactory,
    SetupExecutionEnvironment,
)


class SetupCaseExecutionEnvironment(SetupExecutionEnvironment):
    async def execute(self, function_name: str):
        self.set_cheatcodes(SetupCaseCheatcodeFactory(self.state))

        with self.state.output_recorder.redirect("setup case"):
            await self.perform_execute(function_name)


class SetupCaseCheatcodeFactory(SetupCheatcodeFactory):
    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
    ) -> List[Cheatcode]:
        return [
            *super().build_cheatcodes(syscall_dependencies),
            GivenCheatcode(syscall_dependencies, self._state.config),
            ExampleCheatcode(syscall_dependencies, self._state.config),
            SkipCheatcode(syscall_dependencies),
        ]

    def build_hint_locals(self) -> List[HintLocal]:
        return [
            *super().build_hint_locals(),
            StrategiesHintLocal(),
        ]
