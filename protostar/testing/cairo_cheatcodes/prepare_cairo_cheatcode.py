from typing import Any, Callable, Optional
import asyncio

from protostar.starknet import CheatcodeException
from protostar.starknet.cheaters.contracts import ContractsCheaterException
from protostar.starknet.data_transformer import (
    CairoOrPythonData,
)
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.contract_types import DeclaredContract, PreparedContract


class PrepareCairoCheatcode(CairoCheatcode):
    salt_nonce = 1

    @property
    def name(self) -> str:
        return "prepare"

    def build(self) -> Callable[[Any], Any]:
        return self.prepare

    def prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: Optional[CairoOrPythonData] = None,
        salt: Optional[int] = None,
    ) -> PreparedContract:
        return asyncio.run(
            self._prepare(
                declared=declared, constructor_calldata=constructor_calldata, salt=salt
            )
        )

    async def _prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: Optional[CairoOrPythonData] = None,
        salt: Optional[int] = None,
    ) -> PreparedContract:
        contract_salt = PrepareCairoCheatcode.salt_nonce
        PrepareCairoCheatcode.salt_nonce += 1
        salt = salt or contract_salt
        constructor_calldata = constructor_calldata or []

        try:
            return await self.cheaters.contracts.prepare(
                declared=declared, constructor_calldata=constructor_calldata, salt=salt
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
