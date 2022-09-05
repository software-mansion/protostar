from typing import Any, Callable, List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract
from protostar.starknet.cheatcode import Cheatcode


class DeployCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        cheatable_syscall_internal_calls: List[CallInfo],
    ):
        super().__init__(syscall_dependencies)
        # fixes https://github.com/software-mansion/protostar/issues/398
        self.internal_calls = cheatable_syscall_internal_calls

    @property
    def name(self) -> str:
        return "deploy"

    def build(self) -> Callable[[Any], Any]:
        return self.deploy_prepared

    def deploy_prepared(
        self,
        prepared: PreparedContract,
    ):
        # TODO(mkaput): Reimplement this.
        raise NotImplementedError("Deploy cheatcode is not ported to Cairo 10 yet.")
        # class_hash_bytes = to_bytes(prepared.class_hash)
        # future = asyncio.run_coroutine_threadsafe(
        #     coro=initialize_contract_state(
        #         state=self.state,
        #         class_hash=class_hash_bytes,
        #         contract_address=prepared.contract_address,
        #     ),
        #     loop=self.loop,
        # )
        # future.result()
        #
        # self.execute_constructor_entry_point(
        #     contract_address=prepared.contract_address,
        #     class_hash_bytes=class_hash_bytes,
        #     constructor_calldata=prepared.constructor_calldata,
        # )
        # return DeployedContract(prepared.contract_address)
