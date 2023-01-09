import asyncio
from typing import Any, Optional

from protostar.starknet import Address, RawAddress, CairoOrPythonData
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
        asyncio.run(
            self.cheaters.contracts.invoke(
                function_name=function_name,
                calldata=calldata,
                contract_address=Address.from_user_input(contract_address),
            )
        )
