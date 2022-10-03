import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from starknet_py.net.signer import BaseSigner
from typing_extensions import NotRequired, Protocol

from protostar.starknet import (
    Cheatcode,
    CheatcodeException,
    KeywordOnlyArgumentCheatcodeException,
)
from protostar.starknet_gateway import Fee, GatewayFacade
from protostar.starknet_gateway.gateway_facade import CompilationOutputNotFoundException

from ..migrator_contract_identifier_resolver import MigratorContractIdentifierResolver
from .network_config import CheatcodeNetworkConfig, ValidatedCheatcodeNetworkConfig


@dataclass
class DeclaredContract:
    class_hash: int


class DeclareCheatcodeProtocol(Protocol):
    def __call__(
        self, contract_path_str: str, *args, config: Optional[Any] = None
    ) -> DeclaredContract:
        ...


class DeclareCheatcodeNetworkConfig(CheatcodeNetworkConfig):
    max_fee: NotRequired[Fee]


@dataclass
class ValidatedDeclareCheatcodeNetworkConfig(ValidatedCheatcodeNetworkConfig):
    @classmethod
    def from_declare_cheatcode_network_config(
        cls, config: Optional[DeclareCheatcodeNetworkConfig]
    ) -> "ValidatedDeclareCheatcodeNetworkConfig":
        if config is None:
            return cls()
        validated_network_config = ValidatedCheatcodeNetworkConfig.from_dict(config)
        return cls(
            wait_for_acceptance=validated_network_config.wait_for_acceptance,
            max_fee=config.get("max_fee", None),
        )

    max_fee: Optional[Fee] = None


class MigratorDeclareCheatcode(Cheatcode):
    @dataclass
    class Config:
        signer: Optional[BaseSigner] = None
        token: Optional[str] = None
        account_address: Optional[str] = None

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        migrator_contract_identifier_resolver: MigratorContractIdentifierResolver,
        config: "Config",
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._migrator_contract_identifier_resolver = (
            migrator_contract_identifier_resolver
        )

    @property
    def name(self) -> str:
        return "declare"

    def build(self) -> DeclareCheatcodeProtocol:
        return self._declare

    def _declare(
        self,
        contract_path_str: str,
        *args,
        config: Optional[DeclareCheatcodeNetworkConfig] = None,
    ) -> DeclaredContract:
        contract_identifier = contract_path_str
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = ValidatedDeclareCheatcodeNetworkConfig.from_declare_cheatcode_network_config(
            config
        )
        compiled_contract_path = self._migrator_contract_identifier_resolver.resolve(
            contract_identifier
        )
        try:
            if self._config.signer and self._config.account_address is not None:
                if validated_config.max_fee is None:
                    raise CheatcodeException(
                        self, 'config["max_fee"] is required for transactions V1'
                    )
                response = asyncio.run(
                    self._gateway_facade.declare(
                        compiled_contract_path=compiled_contract_path,
                        account_address=self._config.account_address,
                        signer=self._config.signer,
                        token=self._config.token,
                        wait_for_acceptance=validated_config.wait_for_acceptance,
                        max_fee=validated_config.max_fee,
                    )
                )
            else:
                response = asyncio.run(
                    self._gateway_facade.declare_v0(
                        compiled_contract_path=compiled_contract_path,
                        token=self._config.token,
                        wait_for_acceptance=validated_config.wait_for_acceptance,
                    )
                )
            return DeclaredContract(
                class_hash=response.class_hash,
            )
        except CompilationOutputNotFoundException as ex:
            raise CheatcodeException(self, ex.message) from ex
