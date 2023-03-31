# pylint: disable=duplicate-code
from typing import List

from protostar.cairo import HintLocal
from protostar.cairo_testing import CairoTestExecutionState
from protostar.cheatable_starknet.callable_hint_locals import (
    StoreHintLocal,
    InvokeHintLocal,
    CallHintLocal,
    DeployContractCairo0HintLocal,
    PrankHintLocal,
    RollHintLocal,
    WarpHintLocal,
    DeployCairo0HintLocal,
    PrepareCairo0HintLocal,
    DeclareCairo0HintLocal,
    DeclareHintLocal,
    StopWarpHintLocal,
    StopRollHintLocal,
    SendMessageToL2HintLocal,
    ExpectEventsHintLocal,
    LoadHintLocal,
    MockCallHintLocal,
    ExpectCallHintLocal,
    AssertExpectCallHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.stop_prank_hint_local import (
    StopPrankHintLocal,
)
from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.controllers import (
    StorageController,
    ContractsController,
    BlockInfoController,
    ExpectCallController,
)
from protostar.cheatable_starknet.controllers.expect_events_controller import (
    ExpectEventsController,
)
from protostar.compiler import Cairo0ProjectCompiler
from protostar.compiler.project_compiler import ProjectCompiler
from protostar.testing import Hook


class CairoSharedHintLocalFactory:
    def __init__(
        self,
        cheatable_state: CheatableCachedState,
        cairo0_project_compiler: Cairo0ProjectCompiler,
        project_compiler: ProjectCompiler,
        test_finish_hook: Hook,
        test_execution_state: CairoTestExecutionState,
    ):
        self.cheatable_state = cheatable_state
        self.cairo0_project_compiler = cairo0_project_compiler
        self.project_compiler = project_compiler
        self._test_finish_hook = test_finish_hook
        self._test_execution_state = test_execution_state

    def build_hint_locals(self) -> List[HintLocal]:
        block_info_controller = BlockInfoController(
            cheatable_state=self.cheatable_state
        )
        contracts_controller = ContractsController(cheatable_state=self.cheatable_state)
        storage_controller = StorageController(cheatable_state=self.cheatable_state)

        declare_cheatcode = DeclareHintLocal(
            contracts_controller=contracts_controller,
            project_compiler=self.project_compiler,
        )
        declare_cairo0_cheatcode = DeclareCairo0HintLocal(
            project_compiler=self.cairo0_project_compiler,
            contracts_controller=contracts_controller,
        )
        prepare_cairo0_cheatcode = PrepareCairo0HintLocal(
            contracts_controller=contracts_controller,
        )
        deploy_cairo0_cheatcode = DeployCairo0HintLocal(
            contracts_controller=contracts_controller,
        )

        expect_call_controller = ExpectCallController(
            test_finish_hook=self._test_finish_hook,
            cheatable_state=self._test_execution_state.cheatable_state,
        )

        return [
            WarpHintLocal(block_info_controller=block_info_controller),
            RollHintLocal(block_info_controller=block_info_controller),
            StopWarpHintLocal(block_info_controller=block_info_controller),
            StopRollHintLocal(block_info_controller=block_info_controller),
            PrankHintLocal(contracts_controller=contracts_controller),
            StopPrankHintLocal(contracts_controller=contracts_controller),
            SendMessageToL2HintLocal(contracts_controller=contracts_controller),
            declare_cheatcode,
            declare_cairo0_cheatcode,
            deploy_cairo0_cheatcode,
            prepare_cairo0_cheatcode,
            DeployContractCairo0HintLocal(
                declare_cheatcode=declare_cairo0_cheatcode,
                prepare_cheatcode=prepare_cairo0_cheatcode,
                deploy_cheatcode=deploy_cairo0_cheatcode,
            ),
            CallHintLocal(
                contracts_controller=contracts_controller,
                expect_call_controller=expect_call_controller,
            ),
            InvokeHintLocal(contracts_controller=contracts_controller),
            StoreHintLocal(storage_controller=storage_controller),
            LoadHintLocal(storage_controller=storage_controller),
            ExpectEventsHintLocal(
                controller=ExpectEventsController(
                    test_finish_hook=self._test_finish_hook,
                    test_execution_state=self._test_execution_state,
                    cheatable_state=self._test_execution_state.cheatable_state,
                ),
            ),
            MockCallHintLocal(controller=contracts_controller),
            ExpectCallHintLocal(controller=expect_call_controller),
            AssertExpectCallHintLocal(controller=expect_call_controller),
        ]


class CairoSetupHintLocalFactory:
    def __init__(self, shared_hint_local_factory: CairoSharedHintLocalFactory):
        self._shared_hint_local_factory = shared_hint_local_factory

    def build_hint_locals(self) -> list[HintLocal]:
        return self._shared_hint_local_factory.build_hint_locals()


class CairoTestHintLocalFactory:
    def __init__(self, shared_hint_local_factory: CairoSharedHintLocalFactory):
        self._shared_hint_local_factory = shared_hint_local_factory

    def build_hint_locals(self) -> list[HintLocal]:
        return self._shared_hint_local_factory.build_hint_locals()
