from typing import Callable


from protostar.cheatable_starknet.controllers.expect_call_controller import (
    ExpectCallController,
    ExpectedCall,
)
from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.starknet import RawAddress, Address
from protostar.starknet.selector import Selector
from protostar.starknet.data_transformer import CairoData


class ExpectCallHintLocal(CallableHintLocal):
    def __init__(
        self,
        controller: ExpectCallController,
    ):
        self._controller = controller

    @property
    def name(self) -> str:
        return "expect_call"

    def _build(self) -> Callable:
        return self.expect_call

    def expect_call(self, address: RawAddress, fn_name: str, calldata: CairoData):
        self._controller.add_expected_call(
            expected_call=ExpectedCall(
                address=Address.from_user_input(address),
                fn_selector=Selector(fn_name),
                calldata=calldata,
            )
        )
