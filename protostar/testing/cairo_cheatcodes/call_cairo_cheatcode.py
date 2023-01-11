import asyncio
from typing import Callable, Optional

from protostar.starknet import RawAddress, Address
from protostar.starknet.forkable_starknet import ForkableStarknet
from protostar.starknet.data_transformer import CairoOrPythonData, CairoData
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
        return self.call

    def call(
        self,
        contract_address: RawAddress,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        return asyncio.run(
            self._use_case.execute(
                Address.from_user_input(contract_address),
                function_name,
                calldata,
            )
        )
