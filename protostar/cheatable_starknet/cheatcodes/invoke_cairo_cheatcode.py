import asyncio
from typing import Any, Optional

from protostar.cheatable_starknet.cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.cheatable_starknet.cheaters.contracts import ContractsCheaterException
from protostar.starknet import (
    Address,
    RawAddress,
    CairoOrPythonData,
    CheatcodeException,
    Selector,
)


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
            entry_point_selector=Selector(function_name),
            calldata=calldata,
            contract_address=Address.from_user_input(contract_address),
        )

    def _invoke(
        self,
        contract_address: Address,
        entry_point_selector: Selector,
        calldata: Optional[CairoOrPythonData] = None,
    ):
        try:
            asyncio.run(
                self.cheaters.contracts.invoke(
                    contract_address=contract_address,
                    entry_point_selector=entry_point_selector,
                    calldata=calldata,
                    cheaters=self.cheaters,
                )
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
