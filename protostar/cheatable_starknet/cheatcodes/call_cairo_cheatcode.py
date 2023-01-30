import asyncio
from typing import Callable, Optional

from protostar.starknet import CheatcodeException, RawAddress, Address
from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.starknet.data_transformer import CairoOrPythonData, CairoData
from protostar.starknet.selector import Selector
from protostar.cheatable_starknet.controllers.contracts import ContractsCheaterException


class CallCairoCheatcode(CairoCheatcode):
    @property
    def name(self) -> str:
        return "call"

    def _build(
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
                entry_point_selector=Selector(function_name),
                calldata=calldata,
            )
        )

    async def _call(
        self,
        contract_address: Address,
        entry_point_selector: Selector,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        try:
            return await self.controllers.contracts.call(
                contract_address=contract_address,
                entry_point_selector=entry_point_selector,
                calldata=calldata,
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
