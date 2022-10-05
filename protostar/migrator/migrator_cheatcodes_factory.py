from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from starknet_py.net.signer import BaseSigner
from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.migrator.cheatcodes.migrator_call_cheatcode import MigratorCallCheatcode
from protostar.migrator.cheatcodes.migrator_declare_cheatcode import (
    MigratorDeclareCheatcode,
)
from protostar.migrator.cheatcodes.migrator_deploy_contract_cheatcode import (
    MigratorDeployContractCheatcode,
)
from protostar.migrator.cheatcodes.migrator_invoke_cheatcode import (
    MigratorInvokeCheatcode,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet.hint_local import HintLocal
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.starknet_compilation import StarknetCompiler

from .migrator_contract_identifier_resolver import MigratorContractIdentifierResolver


class MigratorCheatcodeFactory(CheatcodeFactory):
    @dataclass
    class Config:
        account_address: Optional[str] = None
        token: Optional[str] = None

    def __init__(
        self,
        starknet_compiler: StarknetCompiler,
        gateway_facade: GatewayFacade,
        migrator_contract_identifier_resolver: MigratorContractIdentifierResolver,
        compiled_contracts_dir: Path,
        config: "MigratorCheatcodeFactory.Config",
        signer: Optional[BaseSigner] = None,
    ) -> None:
        super().__init__()
        self.gateway_facade = gateway_facade
        self._starknet_compiler = starknet_compiler
        self._migrator_contract_identifier_resolver = (
            migrator_contract_identifier_resolver
        )
        self._signer = signer
        self._config = config
        self._compiled_contracts_dir = compiled_contracts_dir

    def build_cheatcodes(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        assert self._starknet_compiler is not None
        assert self._config is not None

        return [
            MigratorDeclareCheatcode(
                syscall_dependencies,
                self.gateway_facade,
                migrator_contract_identifier_resolver=self._migrator_contract_identifier_resolver,
                build_output_dir=self._compiled_contracts_dir,
                config=MigratorDeclareCheatcode.Config(
                    token=self._config.token,
                    signer=self._signer,
                    account_address=self._config.account_address,
                ),
            ),
            MigratorDeployContractCheatcode(
                syscall_dependencies,
                self.gateway_facade,
                build_output_dir=self._compiled_contracts_dir,
                migrator_contract_identifier_resolver=self._migrator_contract_identifier_resolver,
                config=MigratorDeployContractCheatcode.Config(token=self._config.token),
            ),
            MigratorCallCheatcode(syscall_dependencies, self.gateway_facade),
            MigratorInvokeCheatcode(
                syscall_dependencies=syscall_dependencies,
                gateway_facade=self.gateway_facade,
                signer=self._signer,
                account_address=self._config.account_address,
            ),
        ]

    def build_hint_locals(self) -> List[HintLocal]:
        return []
