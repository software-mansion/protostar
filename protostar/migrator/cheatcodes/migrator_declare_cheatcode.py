import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any
from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import (
    CheatcodeException,
    KeywordOnlyArgumentCheatcodeException,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway import GatewayFacade
from protostar.starknet_gateway.gateway_facade import CompilationOutputNotFoundException

from .network_config import CheatcodeNetworkConfig, ValidatedCheatcodeNetworkConfig


@dataclass
class DeclaredContract:
    class_hash: int


class DeclareCheatcodeProtocol(Protocol):
    def __call__(
        self, contract_path_str: str, *args, config: Optional[Any] = None
    ) -> DeclaredContract:
        ...


class MigratorDeclareCheatcode(Cheatcode):
    @dataclass
    class Config:
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

    def _declare(
        self,
        contract_path_str: str,
        *args,
        config: Optional[CheatcodeNetworkConfig] = None,
    ) -> DeclaredContract:
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(
            config or CheatcodeNetworkConfig()
        )

        try:
            response = asyncio.run(
                self._gateway_facade.declare(
                    compiled_contract_path=Path(contract_path_str),
                    token=self._config.token,
                    wait_for_acceptance=validated_config.wait_for_acceptance,
                )
            )

            return DeclaredContract(
                class_hash=response.class_hash,
            )

        except CompilationOutputNotFoundException as ex:
            raise CheatcodeException(
                cheatcode_name=self.name, message=ex.message
            ) from ex
