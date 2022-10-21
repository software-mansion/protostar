from typing import TYPE_CHECKING, Callable

from protostar.starknet.cheatcode import Cheatcode
from protostar.testing.hook import Hook
from protostar.testing.test_environment_exceptions import ExpectedCallException

if TYPE_CHECKING:
    from protostar.starknet.forkable_starknet import ForkableStarknet


class ExpectCallCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        starknet: "ForkableStarknet",
        finish_hook: Hook,
        contract_address: int,
    ):
        super().__init__(syscall_dependencies)
        self.starknet = starknet
        self.finish_hook = finish_hook
        self.contract_address = contract_address

    @property
    def name(self) -> str:
        return "expect_call"

    def build(self) -> Callable[[int, list[int]], None]:
        return self.expect_call

    def expect_call(self, address: int, calldata: list[int]) -> None:
        def callback():
            exists = False
            call_entries = self.cheatable_state.contract_calls.get(address)
            if call_entries:
                for call_entry in call_entries:
                    # check if calldata matches exactly
                    if call_entry == calldata:
                        exists = True
                        break
                    # check if calldata matches partially
                    if call_entry and set(call_entry) <= set(calldata):
                        exists = True
                        break
            if not exists:
                raise ExpectedCallException(address=address, calldata=calldata)

        self.finish_hook.on(callback)
