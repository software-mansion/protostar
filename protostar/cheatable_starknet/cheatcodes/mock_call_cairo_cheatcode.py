import asyncio
from typing import Callable

from protostar.starknet import CheatcodeException
from protostar.cheatable_starknet.cheaters.contracts import ContractsCheaterException
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet import RawAddress, Address


class MockCallCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "mock_call"

    def build(
        self,
    ) -> Callable[[RawAddress, str, CairoOrPythonData], Callable]:
        return self.mock_call

    def mock_call(
        self,
        contract_address: RawAddress,
        function_name: str,
        ret_data: CairoOrPythonData,
    ) -> Callable:
        return asyncio.run(
            self._mock_call(
                contract_address=Address.from_user_input(contract_address),
                function_name=function_name,
                ret_data=ret_data,
            )
        )

    async def _mock_call(
        self,
        contract_address: Address,
        function_name: str,
        ret_data: CairoOrPythonData,
    ) -> Callable:
        try:
            return await self.cheaters.mocks.mock_call(
                contract_address=contract_address,
                function_name=function_name,
                ret_data=ret_data,
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
