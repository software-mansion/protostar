from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class ProtostarProject:
    libs_path: Path

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarProject":
        return cls(libs_path=Path(raw_dict["libs_path"]))
