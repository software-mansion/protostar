import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import GatewayFacade


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

    def build(self) -> Callable:
        return self._declare

    def _declare(self, contract_path: Path):
        asyncio.run(
            self._gateway_facade.declare(
                compiled_contract_path=contract_path,
                gateway_url=self._config.gateway_url,
                signature=self._config.signature,
                token=self._config.token,
            )
        )
