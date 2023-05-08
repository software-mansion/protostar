import asyncio
import json
from pathlib import Path
from typing import Callable, Tuple

from starkware.starknet.services.api.contract_class.contract_class import (
    ContractClass,
    CompiledClass,
)

from protostar.cairo.cairo_bindings import (
    compile_starknet_contract_to_sierra_from_path,
    compile_starknet_contract_to_casm_from_path,
    CairoBindingException,
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

            compiled_class, contract_class = _compile_contract(
                contract_name=contract_name,
            )

            declared_class: DeclaredSierraClass = asyncio.run(
                self._contracts_controller.declare_sierra_contract(
                    contract_class=contract_class,
                    compiled_class=compiled_class,
                )
            )

            return DeclaredContract(class_hash=declared_class.class_hash)

        def _compile_contract(
            contract_name: str,
        ) -> Tuple[CompiledClass, ContractClass]:
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

            contract_class = _make_contract_class(
                contract_name=contract_name, contract_path=contract_path
            )

            compiled_class = _make_compiled_class(
                contract_name=contract_name, contract_path=contract_path
            )

            return compiled_class, contract_class

        def _make_contract_class(contract_name: str, contract_path: Path):
            sierra_compiled = self._compile_to_sierra(
                contract_name=contract_name, contract_path=contract_path
            )

            sierra_compiled = json.loads(sierra_compiled)
            sierra_compiled.pop("sierra_program_debug_info", None)
            sierra_compiled["abi"] = json.dumps(sierra_compiled["abi"])

            return ContractClass.load(sierra_compiled)

        def _make_compiled_class(contract_name: str, contract_path: Path):
            casm_compiled = self._compile_to_casm(
                contract_name=contract_name, contract_path=contract_path
            )

            return CompiledClass.loads(casm_compiled)

        return declare

    def _compile_to_sierra(self, contract_name: str, contract_path: Path):
        try:
            sierra_compiled = compile_starknet_contract_to_sierra_from_path(
                contract_path
            )

            if sierra_compiled is None:
                raise TypeError
        except (CairoBindingException, TypeError) as ex:
            raise CheatcodeException(
                self, f"Compilation of contract {contract_name} to sierra failed"
            ) from ex
        return sierra_compiled

    def _compile_to_casm(self, contract_name: str, contract_path: Path):
        try:
            casm_compiled = compile_starknet_contract_to_casm_from_path(contract_path)

            if casm_compiled is None:
                raise TypeError
        except (CairoBindingException, TypeError) as ex:
            raise CheatcodeException(
                self, f"Compilation of contract {contract_name} to casm failed"
            ) from ex
        return casm_compiled
