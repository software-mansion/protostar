from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from protostar.protostar_toml.sections._protostar_toml_section import (
    ProtostarTOMLSection,
)


@dataclass
class ProtostarProject(ProtostarTOMLSection):
    libs_path: Path

    @staticmethod
    def get_name() -> str:
        return "project"

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarProject":
        return cls(libs_path=Path(raw_dict["libs_path"]))

    def to_dict(self) -> "ProtostarTOMLSection.Dict":
        result: "ProtostarTOMLSection.Dict" = {}

        result["libs_path"] = str(self.libs_path)

        return result
