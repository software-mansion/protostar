from typing import Optional

from protostar.starknet import CompiledContract

from .project_compiler import (
    ContractIdentifier,
    ProjectCompilerConfig,
    ProjectCompilerProtocol,
    ProjectCompiler,
)
from .compiled_contracts_cache import CompiledContractsCache


class ProjectCompilerCachingProxy(ProjectCompilerProtocol):
    def __init__(
        self,
        project_compiler: ProjectCompiler,
        compiled_contracts_cache: CompiledContractsCache,
    ) -> None:
        self._project_compiler = project_compiler
        self._compiled_contracts_cache = compiled_contracts_cache

    def compile_contract_from_contract_identifier(
        self,
        contract_identifier: ContractIdentifier,
        config: Optional[ProjectCompilerConfig] = None,
    ) -> CompiledContract:
        if isinstance(contract_identifier, str):
            return self.compile_contract_from_contract_name(
                contract_name=contract_identifier, config=config
            )
        return self._project_compiler.compile_contract_from_contract_identifier(
            contract_identifier=contract_identifier, config=config
        )

    def compile_contract_from_contract_name(
        self, contract_name: str, config: Optional[ProjectCompilerConfig] = None
    ) -> CompiledContract:
        cached_compiled_contracts = self._compiled_contracts_cache.read(contract_name)
        if cached_compiled_contracts is not None:
            return cached_compiled_contracts
        return self._project_compiler.compile_contract_from_contract_name(
            contract_name=contract_name, config=config
        )
