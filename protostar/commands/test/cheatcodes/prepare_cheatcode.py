from dataclasses import dataclass
from typing import Any, Callable, List

from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.declare_cheatcode import DeclaredContract


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int


class PrepareCheatcode(Cheatcode):
    salt_nonce = 1

    @staticmethod
    def name() -> str:
        return "prepare"

    def build(self) -> Callable[[Any], Any]:
        return self.prepare

    def prepare(
        self, declared: DeclaredContract, constructor_calldata=None
    ) -> PreparedContract:
        constructor_calldata = constructor_calldata or []
        contract_address: int = calculate_contract_address_from_hash(
            salt=PrepareCheatcode.salt_nonce,
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=self.contract_address,
        )
        PrepareCheatcode.salt_nonce += 1
        return PreparedContract(
            constructor_calldata, contract_address, declared.class_hash
        )
