from typing import List, Optional

from protostar.commands.test.cheatcodes.declare_cheatcode import DeclaredContract
from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract
from protostar.starknet.cheatcode import Cheatcode


class MigratorPrepareCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "prepare"

    def build(self):
        return self._prepare

    @staticmethod
    def _prepare(
        declared: DeclaredContract,
        constructor_calldata: Optional[List[int]] = None,
    ) -> PreparedContract:

        return PreparedContract(
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata or [],
            contract_address=-1,
        )
