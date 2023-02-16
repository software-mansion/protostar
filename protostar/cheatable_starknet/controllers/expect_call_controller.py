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
class ExpectedCall:
    address: Address
    fn_selector: Selector
    calldata: CairoOrPythonData


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
        calldata = expected_call.calldata
        if self._cheatable_state.expected_contract_calls.get(contract_address):
            self._cheatable_state.expected_contract_calls[contract_address].append(
                (int(expected_call.fn_selector), calldata)
            )
        else:
            self._cheatable_state.expected_contract_calls[contract_address] = [
                (int(expected_call.fn_selector), calldata)
            ]

    @staticmethod
    def remove_expected_call_static(
        expected_call: ExpectedCall, cheatable_state: "CheatableCachedState"
    ):
        data_for_address = cheatable_state.expected_contract_calls.get(
            expected_call.address
        )
        if data_for_address is not None:
            for index, (selector, calldata) in enumerate(data_for_address):
                if (
                    selector == int(expected_call.fn_selector)
                    and calldata == expected_call.calldata
                ):
                    del data_for_address[index]
            if not data_for_address:
                del cheatable_state.expected_contract_calls[expected_call.address]

    def remove_expected_call(self, expected_call: ExpectedCall):
        ExpectCallController.remove_expected_call_static(
            expected_call=expected_call, cheatable_state=self._cheatable_state
        )

    def assert_no_expected_calls_left(self):
        try:
            address = next(iter(self._cheatable_state.expected_contract_calls))
            fn_selector, calldata = self._cheatable_state.expected_contract_calls[
                address
            ][0]
            raise ExpectedCallException(
                contract_address=address,
                fn_name=str(fn_selector),
                calldata=calldata,
            )
        except StopIteration:
            pass
