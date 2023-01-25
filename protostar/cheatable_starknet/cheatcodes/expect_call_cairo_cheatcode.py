import asyncio
from typing import Callable, Optional

from protostar.starknet import CheatcodeException
from protostar.starknet import RawAddress, Address
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.cheatable_starknet.cheaters.expects import ExpectsCheaterException


class ExpectCallCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "expect_call"

    def _build(
        self,
    ) -> Callable[[RawAddress, str, Optional[CairoOrPythonData]], Callable]:
        return self.expect_call

    def expect_call(
        self,
        contract_address: RawAddress,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> Callable:
        return asyncio.run(
            self._expect_call(
                contract_address=Address.from_user_input(contract_address),
                function_name=function_name,
                calldata=calldata,
            )
        )

    async def _expect_call(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> Callable:
        try:
            return await self.cheaters.expects.expect_call(
                contract_address=contract_address,
                function_name=function_name,
                calldata=calldata,
            )
        except ExpectsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
