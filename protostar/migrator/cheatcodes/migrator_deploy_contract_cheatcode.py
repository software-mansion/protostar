import asyncio
import collections
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any
from typing_extensions import Protocol

from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.data_transformer import CairoOrPythonData
from protostar.commands.test.test_environment_exceptions import (
    KeywordOnlyArgumentCheatcodeException,
)

<<<<<<< HEAD
from protostar.commands.test.cheatcodes import (
    CheatcodeNetworkConfig,
    get_default_network_config,
)
=======
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
>>>>>>> master


class MigratorDeployContractCheatcode(Cheatcode):
    @dataclass
    class Config:
        token: Optional[str]

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config

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
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        if isinstance(constructor_args, collections.Mapping):
            assert False, "Data Transformer is not supported"

<<<<<<< HEAD
        if not config:
            config = get_default_network_config()
=======
        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(
            config or CheatcodeNetworkConfig()
        )
>>>>>>> master

        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=Path(contract_path),
                inputs=constructor_args,
                token=self._config.token,
<<<<<<< HEAD
                wait_for_acceptance=config["wait_for_acceptance"],
=======
                wait_for_acceptance=validated_config.wait_for_acceptance,
>>>>>>> master
            )
        )

        return DeployedContract(contract_address=response.address)
