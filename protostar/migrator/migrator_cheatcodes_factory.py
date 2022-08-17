from dataclasses import dataclass
from typing import List, Optional

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.migrator.cheatcodes.migrator_call_cheatcode import MigratorCallCheatcode
from protostar.migrator.cheatcodes.migrator_declare_cheatcode import (
    MigratorDeclareCheatcode,
)
from protostar.migrator.cheatcodes.migrator_deploy_contract_cheatcode import (
    MigratorDeployContractCheatcode,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.starknet_compilation import StarknetCompiler


class MigratorCheatcodeFactory(CheatcodeFactory):
    @dataclass
    class Config:
        token: Optional[str] = None

    def __init__(
        self,
        starknet_compiler: StarknetCompiler,
        gateway_facade: GatewayFacade,
        config: "MigratorCheatcodeFactory.Config",
    ) -> None:
        super().__init__()
        self.gateway_facade = gateway_facade
        self._starknet_compiler = starknet_compiler
        self._config = config

    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        assert self._starknet_compiler is not None

        return [
            MigratorDeclareCheatcode(
                syscall_dependencies,
                self.gateway_facade,
                config=MigratorDeclareCheatcode.Config(
                    token=self._config.token,
                ),
            ),
            MigratorDeployContractCheatcode(
                syscall_dependencies,
                self.gateway_facade,
                config=MigratorDeployContractCheatcode.Config(token=self._config.token),
            ),
            MigratorCallCheatcode(syscall_dependencies, self.gateway_facade),
        ]
