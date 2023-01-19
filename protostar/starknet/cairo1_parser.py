from dataclasses import dataclass
from pathlib import Path
from typing import Any
from starkware.cairo.lang.compiler.program import Program, CairoHint, ProgramBase
from starkware.starkware_utils.marshmallow_dataclass_fields import IntAsHex, additional_metadata
import json

@dataclass
class CairoHintCode:
    code: str
    accessible_scopes: list[Any]
    flow_tracking_data: Any

def parse(path: Path):
    with open(path, "r") as f:
        progr = json.loads(f.read())
    prime: int = IntAsHex()._deserialize(progr["prime"], None, None)
    data: list[int] = [IntAsHex()._deserialize(v, None, None) for v in progr["bytecode"]]
    hints: dict[int, list[CairoHintCode]] = {}
    for h in progr["hints"]:
        codes = [CairoHintCode(str(e), [None], None) for e in h[1]]
        hints[int(h[0])] = codes
    builtins = []

    prog = Program(
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
    return (prog, progr["test_entry_points"])


    
