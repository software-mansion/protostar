from dataclasses import dataclass
from typing import List, Optional

from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract
from protostar.migrator.cheatcodes.migrator_declare_cheatcode import (
    MigratorDeclaredContract,
)
from protostar.starknet.cheatcode import Cheatcode


@dataclass
class MigratorPreparedContract(PreparedContract):
    declared_contract: MigratorDeclaredContract


class MigratorPrepareCheatcode(Cheatcode):
    @property
    def name(self) -> str:
        return "prepare"

    def build(self):
        return self._prepare

    @staticmethod
    def _prepare(
        declared: MigratorDeclaredContract,
        constructor_calldata: Optional[List[int]] = None,
    ) -> MigratorPreparedContract:

        return MigratorPreparedContract(
            declared_contract=declared,
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata or [],
            contract_address=-1,
        )
