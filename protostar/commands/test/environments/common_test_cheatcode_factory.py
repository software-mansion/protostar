from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes import (
    DeclareCheatcode,
    DeployCheatcode,
    DeployContractCheatcode,
    LoadCheatcode,
    MaxExamplesCheatcode,
    MockCallCheatcode,
    PrepareCheatcode,
    ReflectCheatcode,
    RollCheatcode,
    StartPrankCheatcode,
    StoreCheatcode,
    WarpCheatcode,
    SkipCheatcode,
)
from protostar.commands.test.cheatcodes.reflect.cairo_struct import CairoStructHintLocal
from protostar.commands.test.starkware.test_execution_state import TestExecutionState
from protostar.commands.test.test_context import TestContextHintLocal
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet.hint_local import HintLocal


class CommonTestCheatcodeFactory(CheatcodeFactory):
    def __init__(self, state: TestExecutionState):
        self._state = state

    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        declare_cheatcode = DeclareCheatcode(
            syscall_dependencies, self._state.starknet_compiler
        )
        prepare_cheatcode = PrepareCheatcode(syscall_dependencies)
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
            MockCallCheatcode(syscall_dependencies),
            WarpCheatcode(syscall_dependencies),
            RollCheatcode(syscall_dependencies),
            StartPrankCheatcode(syscall_dependencies),
            StoreCheatcode(syscall_dependencies),
            LoadCheatcode(syscall_dependencies),
            ReflectCheatcode(syscall_dependencies),
            SkipCheatcode(syscall_dependencies),
            MaxExamplesCheatcode(syscall_dependencies, self._state.config),
        ]

    def build_hint_locals(self) -> List[HintLocal]:
        return [
            TestContextHintLocal(self._state.context),
            CairoStructHintLocal(),
        ]
