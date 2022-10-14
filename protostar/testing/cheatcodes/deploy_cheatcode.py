from typing import Any, Callable, List

from starkware.python.utils import to_bytes
from starkware.starknet.business_logic.execution.objects import CallInfo
from starkware.starknet.services.api.contract_class import EntryPointType

from protostar.migrator.cheatcodes.migrator_deploy_contract_cheatcode import (
    DeployedContract,
)
from protostar.starknet import Cheatcode, CheatcodeException
from protostar.starknet.data_transformer import (
    DataTransformerException,
    to_python_transformer,
)

from .prepare_cheatcode import PreparedContract


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
        self.validate_constructor_args(prepared)
        self.execute_constructor_entry_point(
            class_hash_bytes=to_bytes(prepared.class_hash),
            constructor_calldata=prepared.constructor_calldata,
            contract_address=prepared.contract_address,
        )

    def validate_constructor_args(self, prepared: PreparedContract):
        contract_class = self.state.get_contract_class(to_bytes(prepared.class_hash))

        if not contract_class.abi:
            raise CheatcodeException(self, "Contract ABI was not found")

        transformer = to_python_transformer(contract_class.abi, "constructor", "inputs")
        try:
            transformer(prepared.constructor_calldata)
        except DataTransformerException as dt_exc:
            # starknet.py interprets this call as a cairo -> python transformation, so message has to be modified
            dt_exc.message = dt_exc.message.replace("Output", "Input")
            raise CheatcodeException(
                self,
                f"There was an error while parsing constructor arguments:\n{dt_exc.message}",
            ) from dt_exc
