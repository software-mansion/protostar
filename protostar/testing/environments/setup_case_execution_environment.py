from typing import List

from protostar.cairo import HintLocal
from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import ExampleCheatcode, GivenCheatcode, SkipCheatcode
from protostar.testing.fuzzing.strategies import StrategiesHintLocal

from .setup_execution_environment import (
    SetupCheatcodeFactory,
    SetupExecutionEnvironment,
)
from ...cairo.cairo_function_executor import OffsetOrName


class SetupCaseExecutionEnvironment(SetupExecutionEnvironment):
    async def execute(self, function_identifier: OffsetOrName):
        assert isinstance(
            function_identifier, str
        ), "Only test function names are supported in legacy flow"
        self.set_cheatcodes(SetupCaseCheatcodeFactory(self.state))

        with self.state.output_recorder.redirect("setup case"):
            await self.perform_execute(function_identifier)


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
