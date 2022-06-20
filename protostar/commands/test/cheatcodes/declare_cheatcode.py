import asyncio
from pathlib import Path
from typing import cast
from dataclasses import dataclass


from starkware.python.utils import from_bytes
from starkware.starknet.testing.contract import DeclaredClass
from starkware.starknet.testing.contract_utils import get_abi, get_contract_class


from starkware.starknet.business_logic.internal_transaction import (
    InternalDeclare,
)

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode

@dataclass
class DeclaredContract:
    class_hash: int

class DeclareCheatcode(Cheatcode):

    @staticmethod
    def name() -> str:
        return "declare" 

    def declare(self, contract_path: Path) -> DeclaredContract:
        class_hash = cast(
            int, asyncio.run(self._declare_contract(contract_path)).class_hash
        )
        return DeclaredContract(class_hash)

    async def _declare_contract(self, contract_path):
        contract_class = get_contract_class(
                source=contract_path, cairo_path=self.general_config.cheatcodes_cairo_path
        )

        tx = await InternalDeclare.create_for_testing(
            ffc=self.cheatable_state.ffc,
            contract_class=contract_class,
            chain_id=self.general_config.chain_id.value,
        )

        with self.cheatable_state.copy_and_apply() as state_copy:
            tx_execution_info = await tx.apply_state_updates(
                state=state_copy, general_config=self.general_config
            )

        class_hash = tx_execution_info.call_info.class_hash
        assert class_hash is not None
        return DeclaredClass(
            class_hash=from_bytes(class_hash),
            abi=get_abi(contract_class=contract_class),
        )

