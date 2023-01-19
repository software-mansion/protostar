import asyncio
from typing import Callable, Optional

from protostar.starknet import CheatcodeException
from protostar.starknet.cheater import CheaterException
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet.data_transformer import CairoOrPythonData, CairoData
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
    ) -> CairoData:
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
    ) -> CairoData:
        try:
            return await self.cheaters.contracts.call(
                contract_address=contract_address,
                function_name=function_name,
                calldata=calldata,
                cheaters=self.cheaters,
            )
        except CheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
