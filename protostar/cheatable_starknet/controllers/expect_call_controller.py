from dataclasses import dataclass
from typing import TYPE_CHECKING

from protostar.testing.test_environment_exceptions import ExpectedCallException
from protostar.starknet import CairoOrPythonData, Address
from protostar.starknet.selector import Selector

if TYPE_CHECKING:
    from protostar.testing import Hook
    from protostar.cheatable_starknet.cheatables.cheatable_cached_state import (
        CheatableCachedState,
    )


@dataclass
class FunctionCall:
    fn_selector: Selector
    calldata: CairoOrPythonData

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionCall):
            return NotImplemented
        return self.fn_selector == other.fn_selector and self.calldata == other.calldata


@dataclass
class ExpectedCall:
    address: Address
    call: FunctionCall

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExpectedCall):
            return NotImplemented
        return self.call == other.call and self.address == other.address


class ExpectCallController:
    def __init__(
        self,
        test_finish_hook: "Hook",
        cheatable_state: "CheatableCachedState",
    ) -> None:
        self._test_finish_hook = test_finish_hook
        self._cheatable_state = cheatable_state
        self._test_finish_hook.on(self.assert_no_expected_calls_left)

    def add_expected_call(self, expected_call: ExpectedCall):
        contract_address = Address(int(expected_call.address))
        calldata = expected_call.call.calldata
        if self._cheatable_state.expected_contract_calls.get(contract_address):
            self._cheatable_state.expected_contract_calls[contract_address].append(
                FunctionCall(
                    fn_selector=expected_call.call.fn_selector, calldata=calldata
                )
            )
        else:
            self._cheatable_state.expected_contract_calls[contract_address] = [
                FunctionCall(
                    fn_selector=expected_call.call.fn_selector, calldata=calldata
                ),
            ]

    @staticmethod
    def remove_expected_call_static(
        expected_call_to_remove: ExpectedCall, cheatable_state: "CheatableCachedState"
    ):
        expected_calls = cheatable_state.expected_contract_calls.get(
            expected_call_to_remove.address
        )
        if expected_calls is not None:
            for index, expected_call_item in enumerate(expected_calls):
                if expected_call_item == expected_call_to_remove.call:
                    del expected_calls[index]
            if not expected_calls:
                del cheatable_state.expected_contract_calls[
                    expected_call_to_remove.address
                ]

    def remove_expected_call(self, expected_call: ExpectedCall):
        ExpectCallController.remove_expected_call_static(
            expected_call_to_remove=expected_call, cheatable_state=self._cheatable_state
        )

    def assert_no_expected_calls_left(self):
        try:
            address = next(iter(self._cheatable_state.expected_contract_calls))
            function_call = self._cheatable_state.expected_contract_calls[address][0]
            raise ExpectedCallException(
                contract_address=address,
                fn_name=str(function_call.fn_selector),
                calldata=function_call.calldata,
            )
        except StopIteration:
            pass
