from typing import List

from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.testing.cairo_cheatcodes.declare_cairo_cheatcode import (
    DeclareCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.deploy_cairo_cheatcode import (
    DeployCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.deploy_contract_cairo_cheatcode import (
    DeployContractCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.prepare_cairo_cheatcode import (
    PrepareCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.roll_cairo_cheatcode import RollCairoCheatcode
from protostar.testing.cairo_cheatcodes.warp_cairo_cheatcode import WarpCairoCheatcode
from protostar.testing.cairo_cheatcodes.call_cairo_cheatcode import CallCairoCheatcode
from protostar.testing.cairo_cheatcodes.store_cairo_cheatcode import StoreCairoCheatcode
from protostar.testing.cairo_cheatcodes.load_cairo_cheatcode import LoadCairoCheatcode
from protostar.testing.starkware.test_execution_state import TestExecutionState


class CairoTestCheatcodeFactory:
    def __init__(
        self,
        state: TestExecutionState,
    ):
        self.state = state

    def build_cheatcodes(self) -> List[CairoCheatcode]:
        declare_cheatcode = DeclareCairoCheatcode(
            starknet=self.state.starknet,
            project_compiler=self.state.project_compiler,
        )
        prepare_cheatcode = PrepareCairoCheatcode(
            starknet=self.state.starknet,
        )
        deploy_cheatcode = DeployCairoCheatcode(
            starknet=self.state.starknet,
        )

        return [
            WarpCairoCheatcode(starknet=self.state.starknet),
            RollCairoCheatcode(starknet=self.state.starknet),
            deploy_cheatcode,
            declare_cheatcode,
            prepare_cheatcode,
            DeployContractCairoCheatcode(
                starknet=self.state.starknet,
                declare_cheatcode=declare_cheatcode,
                prepare_cheatcode=prepare_cheatcode,
                deploy_cheatcode=deploy_cheatcode,
            ),
            CallCairoCheatcode(starknet=self.state.starknet),
            StoreCairoCheatcode(starknet=self.state.starknet),
            LoadCairoCheatcode(starknet=self.state.starknet),
        ]
