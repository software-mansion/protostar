# pylint: disable="protected-access"
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from starkware.cairo.lang.compiler.program import Program
from starkware.starkware_utils.marshmallow_dataclass_fields import IntAsHex


@dataclass(frozen=True)
class CairoHintCode:
    code: str
    accessible_scopes: list[Any]
    flow_tracking_data: Any


@dataclass(frozen=True)
class TestCase:
    name: str
    offset: int


@dataclass(frozen=True)
class TestSuite:
    path: Path
    test_cases: list[TestCase]
    program: Program


InstructionPc = int


def build_instruction_pc_to_hint(
    json_dict: Any,
) -> dict[InstructionPc, list[CairoHintCode]]:
    hints: dict[InstructionPc, list[CairoHintCode]] = {}
    for h in json_dict["hints"]:
        codes = [CairoHintCode(str(e), [None], None) for e in h[1]]
        hints[int(h[0])] = codes
    return hints


def parse_test_suite(path: Path, json_raw: Any) -> TestSuite:
    json_dict = json.loads(json_raw)
    prime: int = IntAsHex()._deserialize(json_dict["prime"], None, None)  # pylint
    data: list[int] = [
        IntAsHex()._deserialize(v, None, None) for v in json_dict["bytecode"]
    ]
    instruction_pc_to_hint = build_instruction_pc_to_hint(json_dict)
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

    test_cases = [
        TestCase(name=case["name"], offset=int(case["offset"]))
        for case in json_dict["test_entry_points"]
    ]
    return TestSuite(path=path, test_cases=test_cases, program=program)
