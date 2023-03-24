import asyncio
from typing import Callable

from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
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
from protostar.compiler.project_compiler import ProjectCompiler
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
        return self.declare

    def declare(self, contract: int) -> DeclaredContract:
        contract_identifier = short_string_to_str(contract)

        try:
            contract_class = self._project_compiler.compile_contract_to_sierra_from_contract_identifier(
                contract_identifier
            )

            compiled_class = self._project_compiler.compile_contract_to_casm_from_contract_identifier(
                contract_identifier
            )
        except CompilationException as ex:
            raise CheatcodeException(
                self, f"Compilation of {contract_identifier} failed"
            ) from ex
        except ContractNameNotFoundException as ex:
            raise CheatcodeException(
                self, f"No contract found for the name f{ex.contract_name}"
            ) from ex

        compiled_class_hash = compute_compiled_class_hash(compiled_class)

        declared_class: DeclaredSierraClass = asyncio.run(
            self._contracts_controller.declare_sierra_contract(
                contract_class=contract_class,
                compiled_class=compiled_class,
                compiled_class_hash=compiled_class_hash,
            )
        )

        return DeclaredContract(class_hash=declared_class.class_hash)
