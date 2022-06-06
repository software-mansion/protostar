from dataclasses import dataclass
from typing import Any, Dict

from protostar.protostar_toml.sections._protostar_toml_section import (
    ProtostarTOMLSection,
)
from protostar.utils.protostar_directory import VersionManager, VersionType


@dataclass
class ProtostarConfig(ProtostarTOMLSection):
    protostar_version: VersionType

    @staticmethod
    def get_name() -> str:
        return "config"

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarConfig":
        return cls(
            protostar_version=VersionManager.parse(raw_dict["protostar_version"])
        )

    def to_dict(self) -> "ProtostarTOMLSection.Dict":
        result: ProtostarTOMLSection.Dict = {}
        result["protostar_version"] = str(self.protostar_version)
        return result
