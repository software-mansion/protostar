import json

from starkware.starknet.core.os.contract_class.class_hash import compute_class_hash
from starkware.starknet.core.os.contract_class.compiled_class_hash import (
    compute_compiled_class_hash,
)
from starkware.starknet.services.api.contract_class.contract_class import (
    ContractClass,
    CompiledClass,
)


def make_contract_class(sierra_compiled: str) -> ContractClass:
    sierra_compiled_dict = json.loads(sierra_compiled)
    sierra_compiled_dict.pop("sierra_program_debug_info", None)
    sierra_compiled_dict["abi"] = json.dumps(sierra_compiled_dict["abi"])

    return ContractClass.load(sierra_compiled_dict)


def make_compiled_class(casm_compiled: str) -> CompiledClass:
    return CompiledClass.loads(casm_compiled)


def compute_class_hash_from_sierra_code(sierra_compiled: str) -> int:
    contract_class = make_contract_class(sierra_compiled)
    return compute_class_hash(contract_class)


def compute_compiled_class_hash_from_casm_code(casm_compiled: str) -> int:
    compiled_class = make_compiled_class(casm_compiled)
    return compute_compiled_class_hash(compiled_class)
