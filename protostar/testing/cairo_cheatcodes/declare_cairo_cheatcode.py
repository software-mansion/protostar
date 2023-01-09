import asyncio
from typing import Any, Protocol

from protostar.compiler import ProjectCompiler
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.contract_types import DeclaredContract
from protostar.starknet.forkable_starknet import ForkableStarknet


class DeclareCheatcodeProtocol(Protocol):
    def __call__(
        self,
        contract: str,
        *args: Any,
    ) -> DeclaredContract:
        ...


class DeclareCairoCheatcode(CairoCheatcode):
    def __init__(self, starknet: ForkableStarknet, project_compiler: ProjectCompiler):
        self._starknet = starknet
        self._project_compiler = project_compiler

    @property
    def name(self) -> str:
        return "declare"

    def build(self) -> Any:
        return self.declare

    def declare(self, contract: str) -> DeclaredContract:
        compiled_contract = (
            self._project_compiler.compile_contract_from_contract_identifier(contract)
        )
        declared_class = asyncio.run(
            self._starknet.cheaters.contracts.declare_contract(compiled_contract)
        )

        assert declared_class
        class_hash = declared_class.class_hash

        self._starknet.cheaters.contracts.bind_class_hash_to_contract_identifier(
            class_hash=class_hash,
            contract_identifier=contract,
        )

        return DeclaredContract(class_hash)
