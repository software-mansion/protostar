import asyncio
from typing import Callable, Optional

from protostar.starknet import CheatcodeException, RawAddress, Address, Selector
from protostar.cheatable_starknet.controllers.contracts import (
    ContractsCheaterException,
    ContractsController,
    CallResult,
)
from protostar.cheatable_starknet.controllers import ExpectCallController
from protostar.cheatable_starknet.controllers.expect_call_controller import ExpectedCall
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.cairo.short_string import short_string_to_str, CairoShortString

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
    ) -> Callable[
        [RawAddress, CairoShortString, Optional[CairoOrPythonData]], CallResult
    ]:
        return self.call

    def call(
        self,
        contract_address: RawAddress,
        function_name: CairoShortString,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CallResult:
        return asyncio.run(
            self._call(
                contract_address=Address.from_user_input(contract_address),
                entry_point_selector=Selector(short_string_to_str(function_name)),
                calldata=calldata,
            )
        )

    async def _call(
        self,
        contract_address: Address,
        entry_point_selector: Selector,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CallResult:
        try:
            self._expect_call_controller.remove_expected_call(
                ExpectedCall(
                    address=contract_address,
                    fn_selector=entry_point_selector,
                    calldata=calldata or [],
                )
            )
            return await self._contracts_controller.call(
                contract_address=contract_address,
                entry_point_selector=entry_point_selector,
                calldata=calldata,
            )
        except ContractsCheaterException as exc:
            raise CheatcodeException(self, exc.message) from exc
