from typing import Optional, Dict, Any

from typing_extensions import Protocol

from protostar.commands.test.cheatcodes.declare_cheatcode import DeclareCheatcode
from protostar.commands.test.cheatcodes.deploy_cheatcode import (
    DeployCheatcode,
    DeployedContract,
)
from protostar.commands.test.cheatcodes.prepare_cheatcode import PrepareCheatcode
from protostar.starknet.cheatcode import Cheatcode
from protostar.utils.data_transformer import CairoOrPythonData
from protostar.commands.test.test_environment_exceptions import CheatcodeException


class DeployContractCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract_path: str,
        constructor_args: Optional[CairoOrPythonData] = None,
    ) -> DeployedContract:
        ...


class DeployContractCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        declare_cheatcode: DeclareCheatcode,
        prepare_cheatcode: PrepareCheatcode,
        deploy_cheatcode: DeployCheatcode,
    ):
        super().__init__(syscall_dependencies)
        self._declare_cheatcode = declare_cheatcode
        self._prepare_cheatcode = prepare_cheatcode
        self._deploy_cheatcode = deploy_cheatcode

    @property
    def name(self) -> str:
        return "deploy_contract"

    def build(self) -> DeployContractCheatcodeProtocol:
        return self.deploy_contract

    def deploy_contract(
        self,
        contract_path: str,
        constructor_args: Optional[CairoOrPythonData] = None,
        *args,
        config: Optional[Dict[str, Any]] = None,
    ) -> DeployedContract:
        if len(args) > 0:
            raise CheatcodeException(
                "deploy_contract", "`config` is a keyword only argument."
            )
        declared_contract = self._declare_cheatcode.declare(contract_path)
        prepared_contract = self._prepare_cheatcode.prepare(
            declared_contract, constructor_args
        )
        return self._deploy_cheatcode.deploy_prepared(prepared_contract)
