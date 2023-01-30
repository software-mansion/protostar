# pylint: disable=duplicate-code
from typing import List

from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.cheatcodes.load_cairo_cheatcode import (
    LoadCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.store_cairo_cheatcode import (
    StoreCairoCheatcode,
)
from protostar.cheatable_starknet.controllers.block_info import BlockInfoController
from protostar.cheatable_starknet.controllers.contracts import ContractsController
from protostar.cheatable_starknet.controllers import Controllers
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.cheatable_starknet.cheatcodes.declare_cairo_cheatcode import (
    DeclareCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.deploy_cairo_cheatcode import (
    DeployCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.deploy_contract_cairo_cheatcode import (
    DeployContractCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.invoke_cairo_cheatcode import (
    InvokeCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.prepare_cairo_cheatcode import (
    PrepareCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.roll_cairo_cheatcode import (
    RollCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.warp_cairo_cheatcode import (
    WarpCairoCheatcode,
)
from protostar.cheatable_starknet.cheatcodes.call_cairo_cheatcode import (
    CallCairoCheatcode,
)
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
