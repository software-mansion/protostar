# pylint: disable="protected-access"
from dataclasses import dataclass
from typing import Any

from starkware.cairo.lang.compiler.program import Program
from starkware.starkware_utils.marshmallow_dataclass_fields import IntAsHex

from protostar.cairo.cairo_function_executor import Offset


@dataclass(frozen=True)
class CairoHintCode:
    code: str
    accessible_scopes: list[Any]
    flow_tracking_data: Any


InstructionPc = int


def build_instruction_pc_to_hint(
    casm_json: dict,
) -> dict[InstructionPc, list[CairoHintCode]]:
    hints: dict[InstructionPc, list[CairoHintCode]] = {}
    for h in casm_json["hints"]:
        codes = [CairoHintCode(str(e), [None], None) for e in h[1]]
        hints[int(h[0])] = codes
    return hints


def program_from_casm(casm_json: dict) -> Program:
    prime: int = IntAsHex()._deserialize(casm_json["prime"], None, None)  # pylint
    data: list[int] = [
        IntAsHex()._deserialize(v, None, None) for v in casm_json["bytecode"]
    ]
    instruction_pc_to_hint = build_instruction_pc_to_hint(casm_json)
    builtins = []

    return Program(
        prime=prime,
        data=data,
        hints=instruction_pc_to_hint,
        builtins=builtins,
        main_scope=None,
        identifiers=None,
        reference_manager=None,
        compiler_version="111v",
        attributes=[],
        debug_info=None,
    )  # type: ignore


def get_test_name_to_offset_map_from_casm(casm_json: dict) -> dict[str, Offset]:
    return {
        case["name"]: int(case["offset"]) for case in casm_json["test_entry_points"]
    }
