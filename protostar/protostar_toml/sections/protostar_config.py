from dataclasses import dataclass
from typing import Any, Dict

from protostar.utils.protostar_directory import VersionManager, VersionType


@dataclass
class ProtostarConfig:
    protostar_version: VersionType

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarConfig":
        return cls(
            protostar_version=VersionManager.parse(raw_dict["protostar_version"])
        )
