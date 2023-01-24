from dataclasses import dataclass
from typing import Any, List, Optional

from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starkware_utils.error_handling import StarkException
from starkware.starknet.testing.contract import StarknetContractFunctionInvocation
from starkware.starknet.business_logic.fact_state.state import ExecutionResourcesManager
from starkware.starknet.business_logic.execution.objects import CallInfo

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
from protostar.starknet import execute_on_state
from protostar.starknet import estimate_gas
from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
from protostar.starknet.cheatcode_factory import CheatcodeFactory

from protostar.testing.starkware.contract_based_test_execution_state import (
    ContractBasedTestExecutionState,
)
from protostar.testing.test_environment_exceptions import (
    StarknetRevertableException,
)


from .common_test_cheatcode_factory import CommonTestCheatcodeFactory
from .execution_environment import ExecutionEnvironment, TestExecutionResult


@dataclass
class PerformExecuteResult:
    starknet_call_info: StarknetCallInfo
    call_info: CallInfo
    resources_manager: ExecutionResourcesManager


class ContractBasedTestExecutionEnvironment(
    ExecutionEnvironment[Optional[TestExecutionResult]]
):
    state: ContractBasedTestExecutionState

    def __init__(self, state: ContractBasedTestExecutionState):
        super().__init__(state)
        self._expect_revert_context = ExpectRevertContext()
        self._finish_hook = Hook()

    async def execute(self, function_name: str) -> Optional[TestExecutionResult]:
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
                if self.state.config.gas_estimation_enabled:
                    estimated_fee = estimate_gas(
                        state=self.state.starknet.state.state,
                        call_info=execution_result.call_info,
                        resources_manager=execution_result.resources_manager,
                        starknet_general_config=self.state.starknet.state.general_config,
                    )
                execution_resources = (
                    ExecutionResourcesSummary.from_execution_resources(
                        execution_result.call_info.execution_resources,
                        estimated_gas=estimated_fee,
                    )
                )
        return execution_resources

    async def perform_execute(
        self,
        function_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> PerformExecuteResult:
        try:
            func = self.state.contract.get_contract_function(function_name)
            invocation: StarknetContractFunctionInvocation = func(*args, **kwargs)
            resources_manager = ExecutionResourcesManager.empty()
            starknet_call_info, call_info = await execute_on_state(
                invocation,
                self.state.starknet.cheatable_state,
                resources_manager=resources_manager,
            )
            return PerformExecuteResult(
                call_info=call_info,
                resources_manager=resources_manager,
                starknet_call_info=starknet_call_info,
            )
        except StarkException as ex:
            raise StarknetRevertableException(
                error_message=StarknetRevertableException.extract_error_messages_from_stark_ex_message(
                    ex.message
                ),
                error_type=ex.code.name,
                code=ex.code.value,
                details=ex.message,
            ) from ex

    # TODO(mkaput): Replace these two with stateless parameters passing to ForkableStarknet.
    @staticmethod
    def set_cheatcodes(cheatcode_factory: CheatcodeFactory):
        CheatableExecuteEntryPoint.cheatcode_factory = cheatcode_factory

    @staticmethod
    def set_profile_flag(value: bool):
        CheatableExecuteEntryPoint.profiling = value

    @staticmethod
    def set_max_steps(value: Optional[int]):
        CheatableExecuteEntryPoint.max_steps = value


class TestCaseCheatcodeFactory(CommonTestCheatcodeFactory):
    def __init__(
        self,
        state: ContractBasedTestExecutionState,
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
