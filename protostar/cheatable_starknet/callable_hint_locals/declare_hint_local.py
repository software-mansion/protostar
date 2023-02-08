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
        contracts_controller: ContractsController,
    ):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "declare"

    def _build(self) -> Any:
        return self.declare

    def declare(self, contract: str) -> DeclaredContract:
        declared_class = asyncio.run(
            self._contracts_controller.declare_contract(contract)
        )

        assert declared_class
        class_hash = declared_class.class_hash

        self._contracts_controller.bind_class_hash_to_contract_identifier(
            class_hash=class_hash,
            contract_identifier=contract,
        )

        return DeclaredContract(class_hash)
