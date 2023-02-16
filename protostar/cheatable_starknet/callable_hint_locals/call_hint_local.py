import asyncio
from typing import Callable, Optional

from protostar.starknet import CheatcodeException, RawAddress, Address
from protostar.cheatable_starknet.controllers.contracts import (
    ContractsCheaterException,
    ContractsController,
)
from protostar.cheatable_starknet.controllers import ExpectCallController
from protostar.cheatable_starknet.controllers.expect_call_controller import (
    ExpectedCall,
    FunctionCall,
)
from protostar.starknet.data_transformer import CairoOrPythonData, CairoData
from protostar.starknet.selector import Selector

from .callable_hint_local import CallableHintLocal


class CallHintLocal(CallableHintLocal):
    def __init__(
        self,
        contracts_controller: ContractsController,
        expect_call_controller: ExpectCallController,
    ):
        self._contracts_controller = contracts_controller
        self._expect_call_controller = expect_call_controller

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
            self._expect_call_controller.remove_expected_call(
                ExpectedCall(
                    address=contract_address,
                    call=FunctionCall(
                        fn_selector=entry_point_selector, calldata=calldata or []
                    ),
                )
            )
            return await self._contracts_controller.call(
                contract_address=contract_address,
                entry_point_selector=entry_point_selector,
                calldata=calldata,
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
