import asyncio
from typing import Callable, Optional

from protostar.starknet import (
    RawAddress,
    Address,
    CheatcodeException,
    ForkableStarknet,
    CairoOrPythonData,
    CairoData,
    DataTransformerException,
)
from protostar.testing.use_cases import CallTestingUseCase

from .cairo_cheatcode import CairoCheatcode


class CallCairoCheatcode(CairoCheatcode):
    def __init__(self, starknet: ForkableStarknet, use_case: CallTestingUseCase):
        super().__init__(starknet)
        self._use_case = use_case

    @property
    def name(self) -> str:
        return "call"

    def build(
        self,
    ) -> Callable[[RawAddress, str, Optional[CairoOrPythonData]], CairoOrPythonData]:
        return self._call

    def _call(
        self,
        contract_address: RawAddress,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        try:
            return asyncio.run(
                self._use_case.execute(
                    Address.from_user_input(contract_address),
                    function_name,
                    calldata,
                )
            )
        except DataTransformerException as ex:
            raise CheatcodeException(
                self,
                f"There was an error while parsing the arguments for the function {function_name}:\n"
                + f"{ex.message}",
            ) from ex
