from typing import Optional, List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    ExpectEventsCheatcode,
    ExpectRevertCheatcode,
    MockCallCheatcode,
    RollCheatcode,
    StartPrankCheatcode,
    StoreCheatcode,
    WarpCheatcode,
)
from protostar.commands.test.cheatcodes.expect_revert_cheatcode import (
    ExpectRevertContext,
)
from protostar.commands.test.environments.execution_environment import (
    ExecutionEnvironment,
)
from protostar.commands.test.environments.setup_execution_environment import (
    SetupCheatcodeFactory,
)
from protostar.commands.test.execution_state import ExecutionState
from protostar.commands.test.starkware import ExecutionResourcesSummary
from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.starkware.cheatcode_factory import (
    CheatcodeFactory,
)
from protostar.utils.data_transformer_facade import DataTransformerFacade
from protostar.utils.hook import Hook


class TestExecutionEnvironment(ExecutionEnvironment):
    def __init__(self, state: ExecutionState):
        super().__init__(state)
        self._expect_revert_context = ExpectRevertContext()
        self._finish_hook = Hook()

    def _cheatcode_factory(self) -> CheatcodeFactory:
        return TestCaseCheatcodeFactory(
            state=self.state,
            expect_revert_context=self._expect_revert_context,
            finish_hook=self._finish_hook,
        )

    async def _invoke(self, function_name: str) -> Optional[ExecutionResourcesSummary]:
        execution_resources: Optional[ExecutionResourcesSummary] = None

        async with self._expect_revert_context.test():
            async with self._finish_hook.run_after():
                execution_resources = await self._call(function_name)

        return execution_resources


class TestCaseCheatcodeFactory(SetupCheatcodeFactory):
    def __init__(
        self,
        state: ExecutionState,
        expect_revert_context: ExpectRevertContext,
        finish_hook: Hook,
    ):
        super().__init__(state)
        self._expect_revert_context = expect_revert_context
        self._finish_hook = finish_hook

    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        data_transformer = DataTransformerFacade(self._state.starknet_compiler)

        return [
            *super().build(syscall_dependencies, internal_calls),
            MockCallCheatcode(syscall_dependencies, data_transformer),
            WarpCheatcode(syscall_dependencies),
            RollCheatcode(syscall_dependencies),
            StartPrankCheatcode(syscall_dependencies),
            StoreCheatcode(syscall_dependencies),
            ExpectRevertCheatcode(
                syscall_dependencies,
                self._expect_revert_context,
            ),
            ExpectEventsCheatcode(
                syscall_dependencies,
                self._state.starknet,
                self._finish_hook,
                data_transformer,
            ),
        ]
