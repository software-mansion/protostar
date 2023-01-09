import asyncio
from typing import Callable, Optional

from protostar.starknet import CheatcodeException
from protostar.starknet.cheaters.contracts import ContractsCheaterException
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet import RawAddress, Address


class CallCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "call"

    def build(
        self,
    ) -> Callable[[RawAddress, str, Optional[CairoOrPythonData]], CairoOrPythonData]:
        return self.call

    def call(
        self,
        contract_address: RawAddress,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        return asyncio.run(
            self._call(
                contract_address=Address.from_user_input(contract_address),
                function_name=function_name,
                calldata=calldata,
            )
        )

    async def _call(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        try:
            return await self.cheaters.contracts.call(
                contract_address=contract_address,
                function_name=function_name,
                calldata=calldata,
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
