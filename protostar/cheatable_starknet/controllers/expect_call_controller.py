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


@dataclass(frozen=True)
class ExpectedCall:
    address: Address
    fn_selector: Selector
    calldata: CairoOrPythonData

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExpectedCall):
            return NotImplemented
        return (
            self.address == other.address
            and self.fn_selector == other.fn_selector
            and self.calldata == other.calldata
        )


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
        if self._cheatable_state.expected_contract_calls.get(contract_address):
            self._cheatable_state.expected_contract_calls[contract_address].append(
                expected_call
            )
        else:
            self._cheatable_state.expected_contract_calls[contract_address] = [
                expected_call
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
                if expected_call_item == expected_call_to_remove:
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
            expected_call = self._cheatable_state.expected_contract_calls[address][0]
            raise ExpectedCallException(
                contract_address=address,
                fn_name=str(expected_call.fn_selector),
                calldata=expected_call.calldata,
            )
        except StopIteration:
            pass
