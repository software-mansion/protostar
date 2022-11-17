import asyncio
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Optional

from typing_extensions import Protocol

from protostar.migrator.migrator_contract_identifier_resolver import (
    MigratorContractIdentifierResolver,
)
from protostar.starknet import Cheatcode, KeywordOnlyArgumentCheatcodeException
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.starknet.data_transformer import CairoOrPythonData

from .network_config import CheatcodeNetworkConfig, ValidatedCheatcodeNetworkConfig


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class DeployContractCheatcodeProtocol(Protocol):
    # pylint bug ?
    # pylint: disable=keyword-arg-before-vararg
    def __call__(
        self,
        contract: str,
        constructor_args: Optional[CairoOrPythonData] = None,
        *args: Any,
        config: Optional[Any] = None,
    ) -> DeployedContract:
        ...


class MigratorDeployContractCheatcode(Cheatcode):
    @dataclass
    class Config:
        token: Optional[str]

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        migrator_contract_identifier_resolver: MigratorContractIdentifierResolver,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._migrator_contract_identifier_resolver = (
            migrator_contract_identifier_resolver
        )

    @property
    def name(self) -> str:
        return "deploy_contract"

    def build(self) -> DeployContractCheatcodeProtocol:
        return self._deploy_contract

    # pylint bug ?
    # pylint: disable=keyword-arg-before-vararg
    def _deploy_contract(
        self,
        contract: str,
        constructor_args: Optional[CairoOrPythonData] = None,
        *args: Any,
        config: Optional[CheatcodeNetworkConfig] = None,
    ) -> DeployedContract:
        logger = getLogger()
        logger.warning(
            "`deploy_contract` migrator cheatcode will be removed in the future release\n"
            "https://docs.starknet.io/docs/Blocks/transactions/#deploy-transaction"
        )

        contract_identifier = contract
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(config)
        compiled_contract_path = self._migrator_contract_identifier_resolver.resolve(
            contract_identifier
        )
        # TODO: Deploy with UDC
        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=compiled_contract_path,
                inputs=constructor_args,
                token=self._config.token,
                wait_for_acceptance=validated_config.wait_for_acceptance,
            )
        )
        return DeployedContract(contract_address=response.address)
