# pylint: disable=duplicate-code
from typing import List

from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.cheatcodes import (
    LoadCairoCheatcode,
    StoreCairoCheatcode,
    CairoCheatcode,
    DeclareCairoCheatcode,
    DeployCairoCheatcode,
    DeployContractCairoCheatcode,
    InvokeCairoCheatcode,
    PrepareCairoCheatcode,
    RollCairoCheatcode,
    WarpCairoCheatcode,
    CallCairoCheatcode,
    PrankCairoCheatcode,
)
from protostar.cheatable_starknet.controllers.block_info import BlockInfoController
from protostar.cheatable_starknet.controllers.contracts import ContractsController
from protostar.cheatable_starknet.controllers import Controllers
from protostar.compiler import ProjectCompiler
from protostar.cheatable_starknet.controllers.storage import StorageController


class CairoSetupCheatcodeFactory:
    def __init__(
        self,
        cheatable_state: CheatableCachedState,
        project_compiler: ProjectCompiler,
    ):
        self.cheatable_state = cheatable_state
        self.project_compiler = project_compiler

    def build_cheatcodes(self) -> List[CairoCheatcode]:
        controllers = Controllers(
            block_info=BlockInfoController(cheatable_state=self.cheatable_state),
            contracts=ContractsController(cheatable_state=self.cheatable_state),
            storage=StorageController(cheatable_state=self.cheatable_state),
        )
        declare_cheatcode = DeclareCairoCheatcode(
            controllers=controllers,
            project_compiler=self.project_compiler,
        )
        prepare_cheatcode = PrepareCairoCheatcode(
            controllers=controllers,
        )
        deploy_cheatcode = DeployCairoCheatcode(
            controllers=controllers,
        )

        return [
            WarpCairoCheatcode(controllers=controllers),
            RollCairoCheatcode(controllers=controllers),
            deploy_cheatcode,
            declare_cheatcode,
            prepare_cheatcode,
            DeployContractCairoCheatcode(
                controllers=controllers,
                declare_cheatcode=declare_cheatcode,
                prepare_cheatcode=prepare_cheatcode,
                deploy_cheatcode=deploy_cheatcode,
            ),
            CallCairoCheatcode(controllers=controllers),
            InvokeCairoCheatcode(
                controllers=controllers,
            ),
            StoreCairoCheatcode(
                controllers=controllers,
            ),
            LoadCairoCheatcode(
                controllers=controllers,
            ),
        ]


class CairoTestCheatcodeFactory:
    def __init__(
        self,
        cheatable_state: CheatableCachedState,
        project_compiler: ProjectCompiler,
    ):
        self.cheatable_state = cheatable_state
        self.project_compiler = project_compiler

    def build_cheatcodes(self) -> List[CairoCheatcode]:
        controllers = Controllers(
            block_info=BlockInfoController(cheatable_state=self.cheatable_state),
            contracts=ContractsController(cheatable_state=self.cheatable_state),
            storage=StorageController(cheatable_state=self.cheatable_state),
        )
        declare_cheatcode = DeclareCairoCheatcode(
            controllers=controllers,
            project_compiler=self.project_compiler,
        )
        prepare_cheatcode = PrepareCairoCheatcode(
            controllers=controllers,
        )
        deploy_cheatcode = DeployCairoCheatcode(
            controllers=controllers,
        )

        return [
            WarpCairoCheatcode(controllers=controllers),
            RollCairoCheatcode(controllers=controllers),
            deploy_cheatcode,
            declare_cheatcode,
            prepare_cheatcode,
            DeployContractCairoCheatcode(
                controllers=controllers,
                declare_cheatcode=declare_cheatcode,
                prepare_cheatcode=prepare_cheatcode,
                deploy_cheatcode=deploy_cheatcode,
            ),
            CallCairoCheatcode(controllers=controllers),
            InvokeCairoCheatcode(
                controllers=controllers,
            ),
            PrankCairoCheatcode(
                controllers=controllers,
            ),
            StoreCairoCheatcode(
                controllers=controllers,
            ),
            LoadCairoCheatcode(
                controllers=controllers,
            ),
        ]
