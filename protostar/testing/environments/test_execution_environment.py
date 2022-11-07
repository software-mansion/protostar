from dataclasses import dataclass
from typing import Any, List, Optional

from protostar.starknet.abi import has_function_parameters
from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import ExpectEventsCheatcode, ExpectRevertCheatcode
from protostar.testing.cheatcodes.expect_revert_cheatcode import ExpectRevertContext
from protostar.testing.hook import Hook
from protostar.testing.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.testing.starkware.test_execution_state import TestExecutionState

from .common_test_cheatcode_factory import CommonTestCheatcodeFactory
from .execution_environment import ExecutionEnvironment


@dataclass
class TestExecutionResult:
    execution_resources: Optional[ExecutionResourcesSummary]


class TestExecutionEnvironment(ExecutionEnvironment[TestExecutionResult]):
    state: TestExecutionState

    def __init__(self, state: TestExecutionState):
        super().__init__(state)
        self._expect_revert_context = ExpectRevertContext()
        self._finish_hook = Hook()

    async def execute(self, function_name: str) -> TestExecutionResult:
        assert not has_function_parameters(
            self.state.contract.abi, function_name
        ), f"{self.__class__.__name__} expects no function parameters."

        self.set_profile_flag(self.state.config.profiling)
        self.set_cheatcodes(
            TestCaseCheatcodeFactory(
                state=self.state,
                expect_revert_context=self._expect_revert_context,
                finish_hook=self._finish_hook,
            )
        )

        with self.state.output_recorder.redirect("test"):
            return TestExecutionResult(
                execution_resources=await self.execute_test_case(function_name)
            )

    async def execute_test_case(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[ExecutionResourcesSummary]:
        execution_resources: Optional[ExecutionResourcesSummary] = None

        async with self._expect_revert_context.test():
            async with self._finish_hook.run_after():
                call_info = await self.perform_execute(function_name, *args, **kwargs)
                execution_resources = (
                    ExecutionResourcesSummary.from_execution_resources(
                        call_info.call_info.execution_resources
                    )
                )

        return execution_resources


class TestCaseCheatcodeFactory(CommonTestCheatcodeFactory):
    def __init__(
        self,
        state: TestExecutionState,
        expect_revert_context: ExpectRevertContext,
        finish_hook: Hook,
    ):
        super().__init__(state)
        self._expect_revert_context = expect_revert_context
        self._finish_hook = finish_hook

    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
    ) -> List[Cheatcode]:
        return [
            *super().build_cheatcodes(syscall_dependencies),
            ExpectRevertCheatcode(
                syscall_dependencies,
                self._expect_revert_context,
            ),
            ExpectEventsCheatcode(
                syscall_dependencies,
                self._state.starknet,
                self._finish_hook,
            ),
        ]
