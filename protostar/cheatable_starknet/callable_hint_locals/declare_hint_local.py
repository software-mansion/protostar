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
from protostar.compiler import CompilationException
from protostar.compiler.project_compiler import (
    ProjectCompiler,
    make_compiled_class,
    make_contract_class,
)
from protostar.compiler.project_compiler_types import ContractIdentifier
from protostar.configuration_file.configuration_file import (
    ContractNameNotFoundException,
)
from protostar.starknet import CheatcodeException


class DeclareHintLocal(CallableHintLocal):
    def __init__(
        self,
        contracts_controller: ContractsController,
        project_compiler: ProjectCompiler,
    ):
        self._contracts_controller = contracts_controller
        self._project_compiler = project_compiler

    @property
    def name(self) -> str:
        return "declare"

    def _build(self) -> Callable:
        def declare(contract: int) -> DeclaredContract:
            contract_identifier = short_string_to_str(contract)

            try:
                compiled_class, contract_class = _get_contract_classes(
                    contract_identifier=contract_identifier,
                )
            except CompilationException as ex:
                raise CheatcodeException(
                    self, f"Compilation of {contract_identifier} failed"
                ) from ex
            except ContractNameNotFoundException as ex:
                raise CheatcodeException(
                    self, f"No contract found for the name {ex.contract_name}"
                ) from ex

            declared_class: DeclaredSierraClass = asyncio.run(
                self._contracts_controller.declare_sierra_contract(
                    contract_class=contract_class,
                    compiled_class=compiled_class,
                )
            )

            return DeclaredContract(class_hash=declared_class.class_hash)

        def _get_contract_classes(
            contract_identifier: ContractIdentifier,
        ) -> Tuple[CompiledClass, ContractClass]:
            sierra_compiled, casm_compiled = self._project_compiler.compile_contract(
                contract_identifier
            )

            return make_contract_class(sierra_compiled), make_compiled_class(casm_compiled)


        return declare
