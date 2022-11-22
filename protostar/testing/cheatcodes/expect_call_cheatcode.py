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

    def build(self) -> Callable[[int, str, list[int]], None]:
        return self.expect_call

    def expect_call(
        self, contract_address: RawAddress, fn_name: str, calldata: list[int]
    ) -> None:
        address = Address.from_user_input(contract_address)

        def callback():
            exists = False
            expected_fn_selector = get_selector_from_name(fn_name)
            call_entries = self.cheatable_state.contract_calls.get(address)
            if call_entries:
                for called_fn_selector, call_entry in call_entries:
                    if (
                        call_entry == calldata
                        and expected_fn_selector == called_fn_selector
                    ):
                        exists = True
                        break
            if not exists:
                raise ExpectedCallException(
                    contract_address=address,
                    fn_name=fn_name,
                    calldata=calldata,
                )

        self.finish_hook.on(callback)
