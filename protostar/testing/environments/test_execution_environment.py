from dataclasses import dataclass
from typing import Any, List, Optional

from protostar.starknet.abi import has_function_parameters
from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.cheatcodes import (
    ExpectEventsCheatcode,
    ExpectCallCheatcode,
    ExpectRevertCheatcode,
)
from protostar.testing.cheatcodes.expect_revert_cheatcode import ExpectRevertContext
from protostar.testing.hook import Hook
from protostar.testing.starkware.execution_resources_summary import (
    ExecutionResourcesSummary,
)
from protostar.testing.starkware.test_execution_state import TestExecutionState
from protostar.starknet import estimate_fee

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
        self.set_max_steps(self.state.config.max_steps)

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
                execution_result = await self.perform_execute(
                    function_name, *args, **kwargs
                )
                estimated_fee = None
                if self.state.config.gas_price:
                    estimated_fee = estimate_fee(
                        state=self.state.starknet.state.state,
                        call_info=execution_result.call_info,
                        resources_manager=execution_result.resources_manager,
                        starknet_general_config=self.state.starknet.state.general_config,
                        gas_price=self.state.config.gas_price,
                    )
                execution_resources = (
                    ExecutionResourcesSummary.from_execution_resources(
                        execution_result.call_info.execution_resources,
                        estimated_fee=estimated_fee,
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
            ExpectCallCheatcode(
                syscall_dependencies,
                self._finish_hook,
            ),
        ]
