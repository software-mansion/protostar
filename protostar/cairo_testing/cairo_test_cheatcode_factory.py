from typing import List, cast

from protostar.cheatable_starknet.cheatable_cached_state import (
    CheatableCachedState,
)
from protostar.cheatable_starknet.cheaters.block_info import BlockInfoCairoCheater
from protostar.cheatable_starknet.cheaters.contracts import ContractsCairoCheater

from protostar.cheatable_starknet.cheaters import (
    CairoCheaters,
)
from protostar.cairo_testing.cairo_test_execution_state import (
    CairoTestExecutionState,
)
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


class CairoTestCheatcodeFactory:
    def __init__(
        self,
        state: CairoTestExecutionState,
    ):
        self.state = state

    def build_cheatcodes(self) -> List[CairoCheatcode]:
        cheatable_state = cast(CheatableCachedState, self.state.starknet.state.state)
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
