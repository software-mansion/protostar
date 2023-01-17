from typing import List, cast

from protostar.starknet.new_arch.cheatable_cairo_cached_state import (
    CheatableCairoCachedState,
)
from protostar.starknet.new_arch.cheaters import (
    BlockInfoCairoCheater,
    ContractsCairoCheater,
    CairoCheaters,
)
from protostar.testing.new_arch.cairo_test_execution_state import (
    CairoTestExecutionState,
)
from protostar.testing.new_arch.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.testing.new_arch.cheatcodes.declare_cairo_cheatcode import (
    DeclareCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.deploy_cairo_cheatcode import (
    DeployCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.deploy_contract_cairo_cheatcode import (
    DeployContractCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.invoke_cairo_cheatcode import (
    InvokeCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.prepare_cairo_cheatcode import (
    PrepareCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.roll_cairo_cheatcode import (
    RollCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.warp_cairo_cheatcode import (
    WarpCairoCheatcode,
)
from protostar.testing.new_arch.cheatcodes.call_cairo_cheatcode import (
    CallCairoCheatcode,
)


class CairoTestCheatcodeFactory:
    def __init__(
        self,
        state: CairoTestExecutionState,
    ):
        self.state = state

    def build_cheatcodes(self) -> List[CairoCheatcode]:
        cheatable_state = cast(
            CheatableCairoCachedState, self.state.starknet.state.state
        )
        cheaters = CairoCheaters(
            block_info=BlockInfoCairoCheater(cheatable_state=cheatable_state),
            contracts=ContractsCairoCheater(cheatable_state=cheatable_state),
        )
        declare_cheatcode = DeclareCairoCheatcode(
            cheaters=cheaters,
            project_compiler=self.state.project_compiler,
        )
        prepare_cheatcode = PrepareCairoCheatcode(
            cheaters=cheaters,
        )
        deploy_cheatcode = DeployCairoCheatcode(
            cheaters=cheaters,
        )

        return [
            WarpCairoCheatcode(cheaters=cheaters),
            RollCairoCheatcode(cheaters=cheaters),
            deploy_cheatcode,
            declare_cheatcode,
            prepare_cheatcode,
            DeployContractCairoCheatcode(
                cheaters=cheaters,
                declare_cheatcode=declare_cheatcode,
                prepare_cheatcode=prepare_cheatcode,
                deploy_cheatcode=deploy_cheatcode,
            ),
            CallCairoCheatcode(cheaters=cheaters),
            InvokeCairoCheatcode(
                cheaters=cheaters,
            ),
        ]
