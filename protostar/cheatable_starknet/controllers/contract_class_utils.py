# type: ignore
import functools
import json
import os
import tempfile
from typing import Any, Dict, List, Optional, Set, Tuple

from starkware.cairo.lang.compiler.preprocessor.flow import FlowTrackingDataActual
from starkware.cairo.lang.compiler.program import CairoHint, HintedProgram
from starkware.cairo.lang.compiler.scoped_name import ScopedName

# from starkware.starknet.compiler.v1.compile import JsonObject, compile_sierra_to_casm
from starkware.starknet.services.api.contract_class.contract_class import (
    CompiledClass,
    CompiledClassEntryPoint,
    ContractClass,
    EntryPointType,
)

CONTRACTS_DIR_PATH = os.path.join(os.path.dirname(__file__), "contracts")

EXPECTED_CASM_FIELDS = set(
    ["bytecode", "prime", "compiler_version", "hints", "entry_points_by_type"]
)


def parse_casm_entry_point(entry_point: Dict[str, Any]) -> CompiledClassEntryPoint:
    """
    Parses a Cairo 1.0 Casm entry point dictionary.
    """
    assert entry_point["builtins"] is not None, "Expecting not-None builitin list."
    return CompiledClassEntryPoint(
        selector=int(entry_point["selector"], 16),
        # TODO(Yoni, 1/5/2023): consider changing the 'offset' field to be dumped as int.
        offset=int(entry_point["offset"]),
        builtins=entry_point["builtins"],
    )


def parse_casm_entry_points(
    entry_points: List[Dict[str, Any]]
) -> List[CompiledClassEntryPoint]:
    """
    Parses a List of Cairo 1.0 Casm entry point dictionaries.
    """
    return [
        parse_casm_entry_point(entry_point=entry_point) for entry_point in entry_points
    ]


def parse_casm_entry_points_by_type(
    entry_point_types: Dict[str, List[Dict[str, Any]]],
) -> Dict[EntryPointType, List[CompiledClassEntryPoint]]:
    """
    Parses a Cairo 1.0 Casm entry point type mapping.
    """
    return {
        EntryPointType[entry_point_type]: parse_casm_entry_points(
            entry_points=entry_points
        )
        for entry_point_type, entry_points in entry_point_types.items()
    }


def parse_hints(hints: List[Tuple[int, List[str]]]) -> Dict[int, List[CairoHint]]:
    """
    Parses Cairo 1.0 casm hints.
    Each hint comprises a two-item List: an id (int) and a List of hint codes (strings).
    The returned CairoHint object takes empty "accessible_scopes" and "flow_tracking_data"
    values as these are only relevant to Cairo-0 programs.
    """
    empty_accessible_scope: List[ScopedName] = []
    empty_flow_tracking_data: FlowTrackingDataActual = FlowTrackingDataActual.new(
        group_alloc=lambda: 0
    )

    def parse_hint_codes(hint_codes: List[str]) -> List[CairoHint]:
        return [
            CairoHint(
                code=hint_code,
                accessible_scopes=empty_accessible_scope,
                flow_tracking_data=empty_flow_tracking_data,
            )
            for hint_code in hint_codes
        ]

    return {
        hint_id: parse_hint_codes(hint_codes=hint_codes)
        for hint_id, hint_codes in hints
    }


def verify_casm_fields(casm_fields: Set[str]):
    # Verify all required fields are present.
    for expected_field in EXPECTED_CASM_FIELDS:
        assert (
            expected_field in casm_fields
        ), f"Casm missing a '{expected_field}' field."
    # Verify all present fields are expected.
    assert len(casm_fields) == len(
        EXPECTED_CASM_FIELDS
    ), f"Casm field mismatch, expected {EXPECTED_CASM_FIELDS}, got {casm_fields}"


JsonObject = dict


def parse_casm(casm: JsonObject) -> CompiledClass:
    """
    Parses Cairo 1.0 casm.
    """
    verify_casm_fields(casm_fields=set(casm.keys()))
    data = [int(value, 16) for value in casm["bytecode"]]
    prime = int(casm["prime"], 16)
    compiler_version = casm["compiler_version"]
    hints = parse_hints(hints=casm["hints"])
    program = HintedProgram(
        prime=prime,
        data=data,
        builtins=[],
        hints=hints,
        compiler_version=compiler_version,
    )
    entry_points_by_type = parse_casm_entry_points_by_type(
        entry_point_types=casm["entry_points_by_type"]
    )
    return CompiledClass(program=program, entry_points_by_type=entry_points_by_type)


def compile_contract_class(contract_class: ContractClass) -> CompiledClass:
    """
    Compiles a contract class to a compiled class.
    """
    # Extract Sierra representation from the contact class.
    sierra = contract_class.dump()
    sierra.pop("abi", None)

    # Create a temporary Sierra file.
    with tempfile.NamedTemporaryFile(mode="w") as sierra_file:
        # Obtain temp file name.
        temp_sierra_file_name = sierra_file.name
        # Write the contract class Sierra representation to the sierra file.
        json.dump(obj=sierra, fp=sierra_file, indent=2)

        # Flush the Sierra content to the file.
        sierra_file.flush()

        # Compile the Sierra file.
        # pylint: disable=undefined-variable
        casm_from_compiled_sierra = compile_sierra_to_casm(
            sierra_path=temp_sierra_file_name
        )

    # Parse the resultant Casm file.
    return parse_casm(casm=casm_from_compiled_sierra)


def get_path(name: str, extension: str, dir_path: Optional[str]):
    if dir_path is None:
        dir_path = CONTRACTS_DIR_PATH

    return os.path.join(dir_path, f"{name}.{extension}")


def load_file(path: str) -> JsonObject:
    with open(path, "r") as fp:
        return json.load(fp)


def get_cairo_path(contract_name: str, dir_path: Optional[str] = None) -> str:
    return get_path(
        name=f"{contract_name}_cairo1", extension="cairo", dir_path=dir_path
    )


def get_casm_path(contract_name: str, dir_path: Optional[str] = None) -> str:
    return get_path(name=contract_name, extension="casm", dir_path=dir_path)


def load_casm(casm_path: str) -> CompiledClass:
    return parse_casm(casm=load_file(path=casm_path))


def get_sierra_path(contract_name: str, dir_path: Optional[str] = None) -> str:
    return get_path(name=contract_name, extension="sierra", dir_path=dir_path)


def load_sierra(sierra_path: str) -> ContractClass:
    sierra = load_file(path=sierra_path)
    sierra.pop("sierra_program_debug_info", None)
    convert_sierra_program_abi_to_string(sierra_program=sierra)
    return ContractClass.load(data=sierra)


@functools.lru_cache(maxsize=None)
def get_compiled_class_by_name(contract_name: str) -> CompiledClass:
    return load_casm(casm_path=get_casm_path(contract_name=contract_name))


@functools.lru_cache(maxsize=None)
def get_contract_class_by_name(contract_name: str) -> ContractClass:
    return load_sierra(sierra_path=get_sierra_path(contract_name=contract_name))


def convert_sierra_program_abi_to_string(sierra_program: Dict[str, Any]):
    if "abi" in sierra_program:
        assert isinstance(sierra_program["abi"], list), "Unexpected ABI type."
        sierra_program["abi"] = json.dumps(obj=sierra_program["abi"], indent=2)
