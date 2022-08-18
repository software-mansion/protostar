import asyncio
import collections
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import \
    KeywordOnlyArgumentCheatcodeException
from protostar.compiler import ProjectCompiler
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.data_transformer import CairoOrPythonData

from ...compiler.project_compiler import ContractIdentifier
from .network_config import (CheatcodeNetworkConfig,
                             ValidatedCheatcodeNetworkConfig)


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
        project_compiler: ProjectCompiler,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._project_compiler = project_compiler

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

        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(config)

        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=Path(contract_path),
                inputs=constructor_args,
                token=self._config.token,
                wait_for_acceptance=validated_config.wait_for_acceptance,
            )
        )

        return DeployedContract(contract_address=response.address)

    def _get_compiled_contract_path(
        self, contract_identifier: ContractIdentifier
    ) -> Path:
        if isinstance(contract_identifier, Path):
            return contract_identifier
        assert False, "Not implemented"
        
