import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from protostar.commands.test.cheatcodes.declare_cheatcode import (
    DeclareCheatcodeProtocol,
    DeclaredContract,
)
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import GatewayFacade
from protostar.starknet_gateway.gateway_facade import CompilationOutputNotFoundException


class MigratorDeclareCheatcode(Cheatcode):
    @dataclass
    class Config:
        gateway_url: str
        signature: Optional[List[str]] = None
        token: Optional[str] = None

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        config: "Config",
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config

    @property
    def name(self) -> str:
        return "declare"

    def build(self) -> DeclareCheatcodeProtocol:
        return self._declare

    def _declare(self, contract_path_str: str) -> DeclaredContract:
        try:
            response = asyncio.run(
                self._gateway_facade.declare(
                    compiled_contract_path=Path(contract_path_str),
                    gateway_url=self._config.gateway_url,
                    signature=self._config.signature,
                    token=self._config.token,
                )
            )

            return DeclaredContract(
                class_hash=response.class_hash,
            )

        except CompilationOutputNotFoundException as ex:
            raise CheatcodeException(
                cheatcode_name=self.name, message=ex.message
            ) from ex
