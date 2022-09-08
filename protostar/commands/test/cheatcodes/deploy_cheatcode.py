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
