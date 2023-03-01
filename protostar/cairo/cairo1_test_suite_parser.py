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
    for hint in casm_json["hints"]:
        codes = [CairoHintCode(str(e), [None], None) for e in hint[1]]
        hints[int(hint[0])] = codes
    return hints


TestName = str


@dataclass
class ProtostarCasm:
    program: Program
    offset_map: dict[TestName, Offset]

    @classmethod
    def from_json(cls, casm_json: dict):
        prime: int = IntAsHex()._deserialize(casm_json["prime"], None, None)  # pylint
        data: list[int] = [
            IntAsHex()._deserialize(v, None, None) for v in casm_json["bytecode"]
        ]
        instruction_pc_to_hint = build_instruction_pc_to_hint(casm_json)
        builtins = []

        program = Program(
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
        offset_map = {
            case["name"]: int(case["offset"]) for case in casm_json["test_entry_points"]
        }
        return cls(program=program, offset_map=offset_map)
