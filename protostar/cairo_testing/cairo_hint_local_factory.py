# pylint: disable=duplicate-code
from typing import List

from protostar.cairo import HintLocal
from protostar.cairo_testing import CairoTestExecutionState
from protostar.cheatable_starknet.callable_hint_locals import (
    StoreHintLocal,
    InvokeHintLocal,
    CallHintLocal,
    DeployContractHintLocal,
    PrankHintLocal,
    RollHintLocal,
    WarpHintLocal,
    DeployHintLocal,
    PrepareHintLocal,
    DeclareHintLocal,
    StopWarpHintLocal,
    StopRollHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.expect_events_cairo_cheatcode import (
    ExpectEventsHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.load_hint_local import (
    LoadHintLocal,
)

from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.controllers import (
    StorageController,
    ContractsController,
    BlockInfoController,
    Controllers,
)
from protostar.cheatable_starknet.controllers.expect_events_controller import (
    ExpectEventsController,
)
from protostar.compiler import ProjectCompiler
from protostar.testing import Hook


class CairoSharedHintLocalFactory:
    def __init__(
        self,
        cheatable_state: CheatableCachedState,
        project_compiler: ProjectCompiler,
        test_finish_hook: Hook,
        test_execution_state: CairoTestExecutionState,
    ):

        self.cheatable_state = cheatable_state
        self.project_compiler = project_compiler
        self._test_finish_hook = test_finish_hook
        self._test_execution_state = test_execution_state

    def build_hint_locals(self) -> List[HintLocal]:
        controllers = Controllers(
            block_info=BlockInfoController(cheatable_state=self.cheatable_state),
            contracts=ContractsController(cheatable_state=self.cheatable_state),
            storage=StorageController(cheatable_state=self.cheatable_state),
        )
        declare_cheatcode = DeclareHintLocal(
            controllers=controllers,
            project_compiler=self.project_compiler,
        )
        prepare_cheatcode = PrepareHintLocal(
            controllers=controllers,
        )
        deploy_cheatcode = DeployHintLocal(
            controllers=controllers,
        )

        return [
            WarpHintLocal(controllers=controllers),
            RollHintLocal(controllers=controllers),
            StopWarpHintLocal(controllers=controllers),
            StopRollHintLocal(controllers=controllers),
            PrankHintLocal(controllers=controllers),
            deploy_cheatcode,
            declare_cheatcode,
            prepare_cheatcode,
            DeployContractHintLocal(
                controllers=controllers,
                declare_cheatcode=declare_cheatcode,
                prepare_cheatcode=prepare_cheatcode,
                deploy_cheatcode=deploy_cheatcode,
            ),
            CallHintLocal(controllers=controllers),
            InvokeHintLocal(
                controllers=controllers,
            ),
            StoreHintLocal(
                controllers=controllers,
            ),
            LoadHintLocal(
                controllers=controllers,
            ),
            ExpectEventsHintLocal(
                controller=ExpectEventsController(
                    test_finish_hook=self._test_finish_hook,
                    test_execution_state=self._test_execution_state,
                    cheatable_state=self._test_execution_state.cheatable_state,
                ),
                controllers=controllers,
            ),
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
