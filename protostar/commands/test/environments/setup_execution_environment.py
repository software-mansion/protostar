from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    DeclareCheatcode,
    PrepareCheatcode,
    DeployCheatcode,
    DeployContractCheatcode,
    MockCallCheatcode,
    WarpCheatcode,
    RollCheatcode,
    StartPrankCheatcode,
    StoreCheatcode,
)
from protostar.commands.test.environments.execution_environment import (
    ExecutionEnvironment,
)
from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.commands.test.starkware.cheatcode_factory import (
    CheatcodeFactory,
    WithDataTransformer,
)


class SetupExecutionEnvironment(ExecutionEnvironment):
    def _cheatcode_factory(self) -> CheatcodeFactory:
        return SetupCheatcodeFactory(self.state)


class SetupCheatcodeFactory(CheatcodeFactory, WithDataTransformer):
    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        declare_cheatcode = DeclareCheatcode(
            syscall_dependencies,
            disable_hint_validation=self.state.disable_hint_validation_in_external_contracts,
            cairo_path=self.state.include_paths,
        )
        prepare_cheatcode = PrepareCheatcode(
            syscall_dependencies, self.data_transformer
        )
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
            MockCallCheatcode(syscall_dependencies, self.data_transformer),
            WarpCheatcode(syscall_dependencies),
            RollCheatcode(syscall_dependencies),
            StartPrankCheatcode(syscall_dependencies),
            StoreCheatcode(syscall_dependencies),
        ]
