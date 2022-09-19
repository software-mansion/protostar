import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from starknet_py.net.signer import BaseSigner
from typing_extensions import Protocol

from protostar.commands.test.test_environment_exceptions import (
    CheatcodeException,
    KeywordOnlyArgumentCheatcodeException,
)
from protostar.compiler import CompiledContractWriter, ProjectCompiler
from protostar.migrator.migrator_datetime_state import MigratorDateTimeState
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
        signer: Optional[BaseSigner] = None
        token: Optional[str] = None

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        project_compiler: ProjectCompiler,
        migrator_datetime_state: MigratorDateTimeState,
        config: "Config",
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config
        self._project_compiler = project_compiler
        self._migrator_datetime_state = migrator_datetime_state

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
        contract_identifier = contract_path_str
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        validated_config = ValidatedCheatcodeNetworkConfig.from_dict(
            config or CheatcodeNetworkConfig()
        )

        compiled_contract_path = self._get_path_to_compiled_contract(
            contract_identifier
        )

        try:
            response = asyncio.run(
                self._gateway_facade.declare(
                    compiled_contract_path=compiled_contract_path,
                    token=self._config.token,
                    wait_for_acceptance=validated_config.wait_for_acceptance,
                    signer=self._config.signer,
                )
            )

            return DeclaredContract(
                class_hash=response.class_hash,
            )

        except CompilationOutputNotFoundException as ex:
            raise CheatcodeException(self, ex.message) from ex

    def _get_path_to_compiled_contract(self, contract_identifier: str) -> Path:
        if "." in contract_identifier:
            return Path(contract_identifier)
        return self._compile_contract_by_contract_name(contract_identifier)

    def _compile_contract_by_contract_name(self, contract_name: str) -> Path:
        contract_class = self._project_compiler.compile_contract_from_contract_name(
            contract_name
        )
        output_file_path = (
            CompiledContractWriter(contract=contract_class, contract_name=contract_name)
            .save(
                output_dir=self._migrator_datetime_state.get_compilation_output_path()
            )
            .compiled_contract_path
        )
        return output_file_path
