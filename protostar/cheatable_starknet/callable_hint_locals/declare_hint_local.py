import asyncio
import json
from pathlib import Path
from typing import Callable

from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    ContractClass,
    CompiledClass,
)

from protostar.cairo.cairo_bindings import (
    compile_starknet_contract_to_casm_from_path,
    compile_starknet_contract_to_sierra_from_path,
)
from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.controllers.contracts import (
    DeclaredContract,
    ContractsController,
    DeclaredSierraClass,
)


class DeclareHintLocal(CallableHintLocal):
    def __init__(self, contracts_controller: ContractsController):
        self._contracts_controller = contracts_controller

    @property
    def name(self) -> str:
        return "declare"

    def _build(self) -> Callable:
        return self.declare

    def declare(self, contract: str) -> DeclaredContract:
        # TODO add this
        # compiled_contract_sierra =  ...
        contract_class = make_contract_class("")

        compiled_contract_sierra = compile_starknet_contract_to_sierra_from_path(
            input_path=Path(contract)
        )
        assert compiled_contract_sierra is not None
        contract_class = make_contract_class(compiled_contract_sierra)

        compiled_contract_casm = compile_starknet_contract_to_casm_from_path(
            input_path=Path(contract)
        )
        assert compiled_contract_casm is not None
        compiled_class = make_compiled_class(compiled_contract_casm)
        compiled_class_hash = compute_compiled_class_hash(compiled_class)

        declared_class: DeclaredSierraClass = asyncio.run(
            self._contracts_controller.declare_sierra_contract(
                contract_class=contract_class,
                compiled_class=compiled_class,
                compiled_class_hash=compiled_class_hash,
            )
        )

        self._contracts_controller.bind_class_hash_to_contract_identifier(
            class_hash=declared_class.class_hash,
            contract_identifier=contract,
        )

        return DeclaredContract(class_hash=declared_class.class_hash)


def make_contract_class(sierra_contract: str) -> ContractClass:
    loaded = json.loads(sierra_contract)
    loaded.pop("sierra_program_debug_info", None)
    loaded["abi"] = json.dumps(loaded["abi"])

    return ContractClass.load(loaded)


def make_compiled_class(casm_contract: str) -> CompiledClass:
    compiled_class = json.loads(casm_contract)
    compiled_class["pythonic_hints"] = compiled_class["hints"]
    compiled_class["hints"] = []

    return CompiledClass.load(compiled_class)
