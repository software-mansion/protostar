# pylint: disable=duplicate-code
from typing import List

from protostar.cairo import HintLocal
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
from protostar.compiler import ProjectCompiler


class CairoSharedHintLocalFactory:
    def __init__(
        self,
        cheatable_state: CheatableCachedState,
        project_compiler: ProjectCompiler,
    ):
        self.cheatable_state = cheatable_state
        self.project_compiler = project_compiler

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
