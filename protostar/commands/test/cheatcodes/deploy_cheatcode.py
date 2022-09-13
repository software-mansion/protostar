from typing import Any, Callable, List

from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.objects import CallInfo
from starkware.starknet.public.abi import CONSTRUCTOR_ENTRY_POINT_SELECTOR
from starkware.starknet.services.api.contract_class import EntryPointType

from protostar.commands.test.cheatcodes.prepare_cheatcode import PreparedContract
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator.cheatcodes.migrator_deploy_contract_cheatcode import (
    DeployedContract,
)
from protostar.starknet.cheatable_execute_entry_point import CheatableExecuteEntryPoint
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
        call = CheatableExecuteEntryPoint.create(
            contract_address=prepared.contract_address,
            entry_point_selector=CONSTRUCTOR_ENTRY_POINT_SELECTOR,
            entry_point_type=EntryPointType.CONSTRUCTOR,
            calldata=prepared.constructor_calldata,
            caller_address=self.caller_address,
        )
        call.parent_syscall_handler_internal_calls = self.internal_calls
        call.execute(
            state=self.state,
            resources_manager=self.resources_manager,
            general_config=self.general_config,
            tx_execution_context=self.tx_execution_context,
        )
