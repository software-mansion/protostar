import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import (
    KeywordOnlyArgumentCheatcodeException,
)
from protostar.migrator.migrator_contract_path_provider import (
    MigratorContractPathProvider,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.data_transformer import CairoOrPythonData

from .network_config import CheatcodeNetworkConfig, ValidatedCheatcodeNetworkConfig


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


class DeployContractCheatcodeProtocol(Protocol):
    # pylint bug ?
    # pylint: disable=keyword-arg-before-vararg
    def __call__(
        self,
        contract_path: str,
        constructor_args: Optional[CairoOrPythonData] = None,
        *args,
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
        migrator_contract_path_provider: MigratorContractPathProvider,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._migrator_contract_path_provider = migrator_contract_path_provider

    @property
    def name(self) -> str:
        return "deploy_contract"

    def build(self) -> DeployContractCheatcodeProtocol:
        return self._deploy_contract

    # pylint bug ?
    # pylint: disable=keyword-arg-before-vararg
    def _deploy_contract(
        self,
        contract_path: str,
        constructor_args: Optional[CairoOrPythonData] = None,
        *args,
        config: Optional[CheatcodeNetworkConfig] = None,
    ) -> DeployedContract:
        contract_identifier = contract_path
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(config)
        compiled_contract_path = (
            self._migrator_contract_path_provider.get_path_to_compiled_contract(
                contract_identifier
            )
        )
        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=compiled_contract_path,
                inputs=constructor_args,
                token=self._config.token,
                wait_for_acceptance=validated_config.wait_for_acceptance,
            )
        )
        return DeployedContract(contract_address=response.address)
