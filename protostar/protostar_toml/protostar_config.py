from dataclasses import dataclass
from typing import Any, Dict

from protostar.protostar_toml.core import (
    InvalidProtostarTOMLException,
    ProtostarTOMLReader,
    ProtostarTOMLSection,
)
from protostar.utils.protostar_directory import VersionManager, VersionType


@dataclass
class ProtostarConfig(ProtostarTOMLSection):
    protostar_version: VersionType

    @staticmethod
    def get_section_name() -> str:
        return "config"

    @classmethod
    def from_protostar_toml(
        cls, protostar_toml: ProtostarTOMLReader
    ) -> "ProtostarConfig":
        section_dict = protostar_toml.get_section(cls.get_section_name())
        if section_dict is None:
            raise InvalidProtostarTOMLException(cls.get_section_name())
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarConfig":
        return cls(
            protostar_version=VersionManager.parse(raw_dict["protostar_version"])
        )

    def to_dict(self) -> "ProtostarTOMLSection.Dict":
        result: ProtostarTOMLSection.Dict = {}
        result["protostar_version"] = str(self.protostar_version)
        return result
