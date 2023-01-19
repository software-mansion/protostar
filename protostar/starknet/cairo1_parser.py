from typing import Tuple
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from starkware.cairo.lang.compiler.program import Program, CairoHint, ProgramBase
from starkware.starkware_utils.marshmallow_dataclass_fields import IntAsHex, additional_metadata
import json

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



def parse_test_suite(path: Path, json_raw: Any) -> TestSuite:
    json_dict = json.loads(json_raw)
    prime: int = IntAsHex()._deserialize(json_dict["prime"], None, None)
    data: list[int] = [IntAsHex()._deserialize(v, None, None) for v in json_dict["bytecode"]]
    hints: dict[int, list[CairoHintCode]] = {}
    for h in json_dict["hints"]:
        codes = [CairoHintCode(str(e), [None], None) for e in h[1]]
        hints[int(h[0])] = codes
    builtins = []

    program = Program(
        prime = prime,
        data = data,
        hints = hints,
        builtins = builtins,
        main_scope=None, 
        identifiers=None,
        reference_manager=None,
        compiler_version="111v",
        attributes=[],
        debug_info=None,
    ) # type: ignore

    test_suites = [
        TestCase(name=case["name"], offset=int(case["offset"]))
        for case in json_dict["test_entry_points"] 
    ]
    return TestSuite(path=path, test_cases=test_suites, program=program)


    
