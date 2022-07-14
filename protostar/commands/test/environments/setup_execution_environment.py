from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    DeclareCheatcode,
    DeployCheatcode,
    DeployContractCheatcode,
    MockCallCheatcode,
    PrepareCheatcode,
    RollCheatcode,
    StartPrankCheatcode,
    StoreCheatcode,
    WarpCheatcode,
)
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_context import TestContextHintLocal
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet.execution_environment import ExecutionEnvironment
from protostar.utils.data_transformer_facade import DataTransformerFacade


class SetupExecutionEnvironment(ExecutionEnvironment[None]):
    state: TestExecutionState

    def __init__(self, state: TestExecutionState):
        super().__init__(state)

    async def invoke(self, function_name: str):
        self.set_cheatcodes(SetupCheatcodeFactory(self.state))
        self.set_custom_hint_locals([TestContextHintLocal(self.state.context)])

        await self.perform_invoke(function_name)


class SetupCheatcodeFactory(CheatcodeFactory):
    def __init__(self, state: TestExecutionState):
        self._state = state

    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        data_transformer = DataTransformerFacade(self._state.starknet_compiler)

        declare_cheatcode = DeclareCheatcode(
            syscall_dependencies,
            disable_hint_validation=self._state.disable_hint_validation_in_external_contracts,
            cairo_path=self._state.include_paths,
        )
        prepare_cheatcode = PrepareCheatcode(syscall_dependencies, data_transformer)
        deploy_cheatcode = DeployCheatcode(syscall_dependencies, internal_calls)
        return [
            declare_cheatcode,
            prepare_cheatcode,
            deploy_cheatcode,
            DeployContractCheatcode(
                syscall_dependencies,
                declare_cheatcode,
                prepare_cheatcode,
                deploy_cheatcode,
            ),
            MockCallCheatcode(
                syscall_dependencies,
                data_transformer,
            ),
            WarpCheatcode(syscall_dependencies),
            RollCheatcode(syscall_dependencies),
            StartPrankCheatcode(syscall_dependencies),
            StoreCheatcode(syscall_dependencies),
        ]
