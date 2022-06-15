from dataclasses import dataclass
from typing import Any, Dict

from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection
from protostar.utils.protostar_directory import VersionManager, VersionType


@dataclass
class ProtostarConfigSection(ProtostarTOMLSection):
    protostar_version: VersionType

    @staticmethod
    def get_section_name() -> str:
        return "config"

    @classmethod
    def get_default(cls, version_manager: VersionManager) -> "ProtostarConfigSection":
        return cls(
            protostar_version=version_manager.protostar_version
            or version_manager.parse("0.0.0")
        )

    @classmethod
    def from_protostar_toml_reader(
        cls, protostar_toml: ProtostarTOMLReader
    ) -> "ProtostarConfigSection":
        section_dict = protostar_toml.get_section(cls.get_section_name())
        if section_dict is None:
            raise InvalidProtostarTOMLException(cls.get_section_name())
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarConfigSection":
        return cls(
            protostar_version=cls._load_version_from_raw_dict(
                raw_dict, "protostar_version"
            )
        )

    def to_dict(self) -> "ProtostarTOMLSection.ParsedProtostarTOML":
        result: ProtostarTOMLSection.ParsedProtostarTOML = {}
        result["protostar_version"] = str(self.protostar_version)
        return result
