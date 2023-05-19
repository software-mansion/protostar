import asyncio
from typing import Callable, Tuple

from starkware.starknet.services.api.contract_class.contract_class import (
    ContractClass,
    CompiledClass,
)
from protostar.cairo.short_string import short_string_to_str
from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers.contracts import (
    DeclaredContract,
    ContractsController,
    DeclaredSierraClass,
)
from protostar.cairo.contract_class import make_contract_class, make_compiled_class
from protostar.compiler.cairo1_contract_compiler import (
    Cairo1ContractCompiler,
    SierraCompilationException,
    CasmCompilationException,
)

from protostar.contract_path_resolver import ContractPathResolver
from protostar.configuration_file.configuration_file import (
    ContractNameNotFoundException,
)
from protostar.starknet import CheatcodeException


class DeclareHintLocal(CallableHintLocal):
    def __init__(
        self,
        contracts_controller: ContractsController,
        contract_path_resolver: ContractPathResolver,
    ):
        self._contracts_controller = contracts_controller
        self._contract_path_resolver = contract_path_resolver

    @property
    def name(self) -> str:
        return "declare"

    def _build(self) -> Callable:
        def declare(contract: int) -> DeclaredContract:
            contract_name = short_string_to_str(contract)

            contract_class, compiled_class = _get_contract_classes(
                contract_name=contract_name,
            )

            declared_class: DeclaredSierraClass = asyncio.run(
                self._contracts_controller.declare_sierra_contract(
                    contract_class=contract_class,
                    compiled_class=compiled_class,
                )
            )

            return DeclaredContract(class_hash=declared_class.class_hash)

        def _get_contract_classes(
            contract_name: str,
        ) -> Tuple[ContractClass, CompiledClass]:
            try:
                contract_path = (
                    self._contract_path_resolver.contract_path_from_contract_name(
                        contract_name
                    )
                )
            except ContractNameNotFoundException as ex:
                raise CheatcodeException(
                    self, f"No contract found for the name {ex.contract_name}"
                ) from ex

            try:
                (
                    sierra_compiled,
                    casm_compiled,
                ) = Cairo1ContractCompiler.compile_contract(
                    contract_name, contract_path
                )
            except SierraCompilationException as ex:
                raise CheatcodeException(
                    self, f"Compilation of contract {contract_name} to sierra failed"
                ) from ex
            except CasmCompilationException as ex:
                raise CheatcodeException(
                    self, f"Compilation of contract {contract_name} to casm failed"
                ) from ex

            return make_contract_class(sierra_compiled), make_compiled_class(
                casm_compiled
            )

        return declare
