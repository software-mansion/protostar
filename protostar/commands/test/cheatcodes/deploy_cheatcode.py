from typing import Any, Callable, List

from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.objects import CallInfo
from starkware.starknet.services.api.contract_class import EntryPointType

from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator.cheatcodes.migrator_deploy_contract_cheatcode import (
    DeployedContract,
)
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
        self.state.deploy_contract(
            contract_address=prepared.contract_address,
            class_hash=to_bytes(prepared.class_hash),
        )

        contract_class = self.state.get_contract_class(
            class_hash=to_bytes(prepared.class_hash)
        )

        has_constructor = len(
            contract_class.entry_points_by_type[EntryPointType.CONSTRUCTOR]
        )
        if has_constructor:
            self.invoke_constructor(prepared)
        elif not has_constructor and prepared.constructor_calldata:
            raise CheatcodeException(
                self,
                "Tried to deploy a contract with constructor calldata, but no constructor was found.",
            )

        return DeployedContract(contract_address=prepared.contract_address)

    def invoke_constructor(self, prepared: PreparedContract):
        self.execute_constructor_entry_point(
            class_hash_bytes=to_bytes(prepared.class_hash),
            constructor_calldata=prepared.constructor_calldata,
            contract_address=prepared.contract_address,
        )
