import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import (
    KeywordOnlyArgumentCheatcodeException,
)
from protostar.compiler import ProjectCompiler
from protostar.compiler.compiled_contract_writer import CompiledContractWriter
from protostar.migrator.migrator_datetime_state import MigratorDateTimeState
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
        project_compiler: ProjectCompiler,
        migrator_datetime_state: MigratorDateTimeState,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._project_compiler = project_compiler
        self._migrator_datetime_state = migrator_datetime_state

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
        compiled_contract_path = self._get_path_to_compiled_contract(
            contract_identifier
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

    def _get_path_to_compiled_contract(self, contract_identifier: str) -> Path:
        if "." in contract_identifier:
            return Path(contract_identifier)
        return self._compile_contract_by_contract_name(contract_identifier)

    def _compile_contract_by_contract_name(self, contract_name: str) -> Path:
        contract_class = self._project_compiler.compile_contract_from_contract_name(
            contract_name
        )
        output_file_path = CompiledContractWriter(
            contract=contract_class, contract_name=contract_name
        ).save_compiled_contract(
            output_dir=self._migrator_datetime_state.get_compilation_output_path()
        )
        return output_file_path
