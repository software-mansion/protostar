from typing import List

from starkware.starknet.business_logic.execution.objects import CallInfo

from protostar.migrator.cheatcodes.migrator_declare_cheatcode import (
    MigratorDeclareCheatcode,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet.cheatcode_factory import CheatcodeFactory
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.starknet_compilation import StarknetCompiler


class MigratorCheatcodeFactory(CheatcodeFactory):
    def __init__(
        self, starknet_compiler: StarknetCompiler, gateway_facade: GatewayFacade
    ) -> None:
        super().__init__()
        self._starknet_compiler = starknet_compiler
        self._gateway_facade = gateway_facade

    def build(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        internal_calls: List[CallInfo],
    ) -> List[Cheatcode]:
        assert self._starknet_compiler is not None

        return [
            MigratorDeclareCheatcode(
                syscall_dependencies,
                self._gateway_facade,
                config=MigratorDeclareCheatcode.Config(gateway_url=""),
            )
        ]
