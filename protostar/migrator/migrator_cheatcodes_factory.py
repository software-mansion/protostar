from dataclasses import dataclass
from typing import List, Optional

from starknet_py.net.signer import BaseSigner
from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.compiler import ProjectCompiler
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

from .migrator_datetime_state import MigratorDateTimeState


class MigratorCheatcodeFactory(CheatcodeFactory):
    @dataclass
    class Config:
        signer: Optional[BaseSigner] = None
        token: Optional[str] = None

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        starknet_compiler: StarknetCompiler,
        gateway_facade: GatewayFacade,
        project_compiler: ProjectCompiler,
        migrator_datetime_state: MigratorDateTimeState,
        config: "MigratorCheatcodeFactory.Config",
    ) -> None:
        super().__init__()
        self.gateway_facade = gateway_facade
        self._starknet_compiler = starknet_compiler
        self._project_compiler = project_compiler
        self._migrator_datetime_state = migrator_datetime_state
        self._config = config

    def build(
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
                config=MigratorDeclareCheatcode.Config(
                    token=self._config.token,
                    signer=self._config.signer,
                ),
            ),
            MigratorDeployContractCheatcode(
                syscall_dependencies,
                self.gateway_facade,
                project_compiler=self._project_compiler,
                migrator_datetime_state=self._migrator_datetime_state,
                config=MigratorDeployContractCheatcode.Config(token=self._config.token),
            ),
            MigratorCallCheatcode(syscall_dependencies, self.gateway_facade),
        ]
