import asyncio
from typing import Any, Protocol

from protostar.cheatable_starknet.controllers.contracts import (
    ContractsController,
    DeclaredContract,
)
from protostar.compiler import ProjectCompiler

from .callable_hint_local import CallableHintLocal


class DeclareCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract: str,
        *args: Any,
    ) -> DeclaredContract:
        ...


class DeclareHintLocal(CallableHintLocal):
    def __init__(
        self,
        project_compiler: ProjectCompiler,
        contracts_controller: ContractsController,
    ):
        self._contracts_controller = contracts_controller
        self._project_compiler = project_compiler

    @property
    def name(self) -> str:
        return "declare"

    def _build(self) -> Any:
        return self.declare

    def declare(self, contract: str) -> DeclaredContract:
        compiled_contract = (
            self._project_compiler.compile_contract_from_contract_identifier(contract)
        )
        declared_class = asyncio.run(
            self._contracts_controller.declare_contract(compiled_contract)
        )
        return DeclaredContract(class_hash=declared_class.class_hash)
