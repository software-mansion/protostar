from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from starkware.starknet.services.api.contract_class import ContractClass

from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.utils.starknet_compilation import StarknetCompiler

ContractName = str
ContractPath = Path
ContractIdentifier = Union[ContractName, ContractPath]


class ProjectContractsCompiler:
    @dataclass
    class Config:
        debug_info = False

    def __init__(
        self,
        starknet_compiler: StarknetCompiler,
        contracts_section: ProtostarContractsSection,
        config: Optional["ProjectContractsCompiler.Config"] = None,
    ) -> None:
        self._starknet_compiler = starknet_compiler
        self._contracts_section = contracts_section
        self._config = config or ProjectContractsCompiler.Config()

    def compile_from_contract_identifier(
        self, contract_identifier: ContractIdentifier
    ) -> ContractClass:
        if isinstance(contract_identifier, Path):
            return self.compile_from_contract_path(contract_path=contract_identifier)
        return self.compile_from_contract_name(contract_identifier)

    def compile_from_contract_path(self, contract_path: Path) -> ContractClass:
        self._contracts_section.assert_contract_path_exists(contract_path)
        return self._starknet_compiler.compile_contract(
            contract_path, add_debug_info=self._config.debug_info
        )

    def compile_from_contract_name(self, contract_name: str) -> ContractClass:
        paths = self._contracts_section.get_contract_paths(contract_name)
        return self._starknet_compiler.compile_contract(
            *paths, add_debug_info=self._config.debug_info
        )
