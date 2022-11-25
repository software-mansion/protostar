from typing import Callable

from starkware.starknet.public.abi import get_selector_from_name

from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.hook import Hook
from protostar.testing.test_environment_exceptions import ExpectedCallException
from protostar.starknet import RawAddress, Address


def generate_expected_call_calldata(
    fn_name: str, calldata: list[int]
) -> tuple[int, list[int]]:
    expected_fn_selector = get_selector_from_name(fn_name)
    return int(str(expected_fn_selector)), calldata


class ExpectCallCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        finish_hook: Hook,
    ):
        super().__init__(syscall_dependencies)
        self.finish_hook = finish_hook

    @property
    def name(self) -> str:
        return "expect_call"

    def build(self) -> Callable[[int, str, list[int]], Callable]:
        return self.expect_call

    def expect_call(
        self, raw_address: RawAddress, fn_name: str, calldata: list[int]
    ) -> Callable:
        contract_address = Address.from_user_input(raw_address)
        selector, calldata = generate_expected_call_calldata(
            fn_name=fn_name, calldata=calldata
        )

        if self.cheatable_state.expected_contract_calls.get(contract_address):
            self.cheatable_state.expected_contract_calls[contract_address].append(
                (selector, calldata)
            )
        else:
            self.cheatable_state.expected_contract_calls[contract_address] = [
                (selector, calldata)
            ]

        def stop_callback():
            data_for_address = self.cheatable_state.expected_contract_calls.get(
                contract_address
            )
            if data_for_address and (selector, calldata) in data_for_address:
                raise Exception("expected call but it didn't happen todo this msg")

        def finish_callback():
            if not self.cheatable_state.expected_contract_calls:
                return
            expected_call_item = self.cheatable_state.expected_contract_calls.get(
                contract_address
            )
            if expected_call_item and (selector, calldata) in expected_call_item:
                raise ExpectedCallException(
                    contract_address=contract_address,
                    fn_name=fn_name,
                    calldata=calldata,
                )

        self.finish_hook.on(finish_callback)

        return stop_callback
