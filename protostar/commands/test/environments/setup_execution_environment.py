from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    DeclareCheatcode,
    DeployCheatcode,
    DeployContractCheatcode,
    PrepareCheatcode,
)
from protostar.commands.test.environments.execution_environment import (
    ExecutionEnvironment,
)
from protostar.commands.test.execution_state import ExecutionState
from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.starkware.cheatcode_factory import CheatcodeFactory
from protostar.utils.data_transformer_facade import DataTransformerFacade


class SetupExecutionEnvironment(ExecutionEnvironment):
    def _cheatcode_factory(self) -> CheatcodeFactory:
        return SetupCheatcodeFactory(self.state)


class SetupCheatcodeFactory(CheatcodeFactory):
    def __init__(self, state: ExecutionState):
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
        ]
