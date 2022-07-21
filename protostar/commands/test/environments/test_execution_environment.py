from typing import Optional, List
from contextlib import redirect_stdout

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    ExpectEventsCheatcode,
    ExpectRevertCheatcode,
)
from protostar.commands.test.cheatcodes.expect_revert_cheatcode import (
    ExpectRevertContext,
)
from protostar.commands.test.environments.setup_execution_environment import (
    SetupCheatcodeFactory,
)
from protostar.commands.test.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_context import TestContextHintLocal
from protostar.commands.test.test_output_recorder import OutputName
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.utils.data_transformer_facade import DataTransformerFacade
from protostar.utils.hook import Hook

from io import StringIO


class TestExecutionEnvironment(
    ExecutionEnvironment[Optional[ExecutionResourcesSummary]]
):
    state: TestExecutionState

    def __init__(self, state: TestExecutionState):
        super().__init__(state)
        self._expect_revert_context = ExpectRevertContext()
        self._finish_hook = Hook()

    async def invoke(
        self, function_name: str, output_name: OutputName
    ) -> Optional[ExecutionResourcesSummary]:
        self.set_cheatcodes(
            TestCaseCheatcodeFactory(
                state=self.state,
                expect_revert_context=self._expect_revert_context,
                finish_hook=self._finish_hook,
            )
        )

        self.set_custom_hint_locals([TestContextHintLocal(self.state.context)])

        execution_resources: Optional[ExecutionResourcesSummary] = None

        async with self._expect_revert_context.test():
            async with self._finish_hook.run_after():
                with redirect_stdout(self.state.output_recorder.record(output_name)):
                    tx_info = await self.perform_invoke(function_name)
                execution_resources = (
                    ExecutionResourcesSummary.from_execution_resources(
                        tx_info.call_info.execution_resources
                    )
                )

        return execution_resources


class TestCaseCheatcodeFactory(SetupCheatcodeFactory):
    def __init__(
        self,
        state: TestExecutionState,
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
