# pylint: disable=duplicate-code
from typing import List

from protostar.cairo import HintLocal
from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.callable_hint_locals.load_hint_local import (
    LoadHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.store_hint_local import (
    StoreHintLocal,
)
from protostar.cheatable_starknet.controllers.block_info import BlockInfoController
from protostar.cheatable_starknet.controllers.contracts import ContractsController
from protostar.cheatable_starknet.controllers import Controllers
from protostar.cheatable_starknet.callable_hint_locals.declare_hint_local import (
    DeclareHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.deploy_hint_local import (
    DeployHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.deploy_contract_hint_local import (
    DeployContractHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.invoke_hint_local import (
    InvokeHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.prepare_hint_local import (
    PrepareHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.roll_hint_local import (
    RollHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.warp_hint_local import (
    WarpHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.call_hint_local import (
    CallHintLocal,
)
from protostar.compiler import ProjectCompiler
from protostar.cheatable_starknet.controllers.storage import StorageController


class CairoSetupHintLocalsFactory:
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
