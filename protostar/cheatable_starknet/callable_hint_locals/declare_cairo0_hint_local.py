import asyncio
from typing import Any, Protocol

from protostar.cheatable_starknet.controllers.contracts import (
    ContractsController,
    DeclaredContract,
)
from protostar.compiler import ProjectCompiler
from protostar.cairo.short_string import CairoShortString, short_string_to_str

from .callable_hint_local import CallableHintLocal


class DeclareCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract: str,
        *args: Any,
    ) -> DeclaredContract:
        ...


class DeclareCairo0HintLocal(CallableHintLocal):
    def __init__(
        self,
        project_compiler: ProjectCompiler,
        contracts_controller: ContractsController,
    ):
        self._contracts_controller = contracts_controller
        self._project_compiler = project_compiler

    @property
    def name(self) -> str:
        return "declare_cairo0"

    def _build(self) -> Any:
        return self.declare_cairo0

    def declare_cairo0(self, contract: CairoShortString) -> DeclaredContract:
        contract_str = short_string_to_str(contract)
        compiled_contract = (
            self._project_compiler.compile_contract_from_contract_identifier(
                contract_str
            )
        )
        declared_class = asyncio.run(
            self._contracts_controller.declare_cairo0_contract(compiled_contract)
        )

        assert declared_class
        class_hash = declared_class.class_hash

        return DeclaredContract(class_hash)
