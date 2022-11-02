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
    ):
        super().__init__(syscall_dependencies)
        self.starknet = starknet
        self.finish_hook = finish_hook

    @property
    def name(self) -> str:
        return "expect_call"

    def build(self) -> Callable[[int, list[int]], None]:
        return self.expect_call

    def expect_call(self, contract_address: int, calldata: list[int]) -> None:
        def callback():
            exists = False
            call_entries = self.cheatable_state.contract_calls.get(contract_address)
            if call_entries:
                for call_entry in call_entries:
                    if call_entry == calldata:
                        exists = True
                        break
            if not exists:
                raise ExpectedCallException(contract_address=contract_address, calldata=calldata)

        self.finish_hook.on(callback)
