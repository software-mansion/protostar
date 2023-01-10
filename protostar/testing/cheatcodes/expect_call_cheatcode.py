from typing import Callable

from starkware.starknet.public.abi import get_selector_from_name

from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.hook import Hook
from protostar.testing.test_environment_exceptions import ExpectedCallException
from protostar.starknet import RawAddress, Address


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
        self, raw_address: RawAddress, function_name: str, calldata: list[int]
    ) -> Callable:
        contract_address = Address.from_user_input(raw_address)
        function_selector = get_selector_from_name(function_name)

        self.cheatable_state.register_expected_call(
            contract_address=contract_address,
            function_selector=function_selector,
            calldata=calldata,
        )

        def stop_callback():
            data_for_address = self.cheatable_state.expected_contract_calls.get(
                contract_address
            )
            if data_for_address and (function_selector, calldata) in data_for_address:
                raise ExpectedCallException(
                    contract_address=contract_address,
                    function_name=function_name,
                    calldata=calldata,
                )

        def finish_callback():
            if not self.cheatable_state.expected_contract_calls:
                return
            expected_call_item = self.cheatable_state.expected_contract_calls.get(
                contract_address
            )
            if (
                expected_call_item
                and (function_selector, calldata) in expected_call_item
            ):
                raise ExpectedCallException(
                    contract_address=contract_address,
                    function_name=function_name,
                    calldata=calldata,
                )

        self.finish_hook.on(finish_callback)

        return stop_callback
