import asyncio
from typing import Any, Optional

from protostar.starknet import (
    Address,
    RawAddress,
    CairoOrPythonData,
    CheatcodeException,
)
from protostar.starknet.cheaters.contracts import ContractsCheaterException
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode


class InvokeCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "invoke"

    def build(self) -> Any:
        return self.invoke

    def invoke(
        self,
        contract_address: RawAddress,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        self._invoke(
            function_name=function_name,
            calldata=calldata,
            contract_address=Address.from_user_input(contract_address),
        )

    def _invoke(
        self,
        contract_address: RawAddress,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        try:
            asyncio.run(
                self.cheaters.contracts.invoke(
                    contract_address=contract_address,
                    function_name=function_name,
                    calldata=calldata,
                )
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
