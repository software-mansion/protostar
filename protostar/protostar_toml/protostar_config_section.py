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
    def from_protostar_toml_reader(
        cls, protostar_toml: ProtostarTOMLReader
    ) -> "ProtostarConfigSection":
        section_dict = protostar_toml.get_section(cls.get_section_name())
        if section_dict is None:
            raise InvalidProtostarTOMLException(cls.get_section_name())
        return cls.from_dict(section_dict)

    @classmethod
    def _load_version_from_raw_dict(
        cls, raw_dict: Dict[str, Any], attribute_name: str
    ) -> VersionType:
        try:
            return VersionManager.parse(raw_dict[attribute_name])
        except TypeError as err:
            raise InvalidProtostarTOMLException(
                cls.get_section_name(), attribute_name
            ) from err

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarConfigSection":
        protostar_version = cls._load_version_from_raw_dict(
            raw_dict, "protostar_version"
        )

        return cls(protostar_version=protostar_version)

    def to_dict(self) -> "ProtostarTOMLSection.TOMLCompatibleDict":
        result: ProtostarTOMLSection.TOMLCompatibleDict = {}
        result["protostar_version"] = str(self.protostar_version)
        return result
