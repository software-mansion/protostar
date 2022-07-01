from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection


@dataclass
class ProtostarProjectSection(ProtostarTOMLSection):
    class Loader(ProtostarTOMLSection.Loader):
        def __init__(self, protostar_toml_reader: ProtostarTOMLReader) -> None:
            self._protostar_toml_reader = protostar_toml_reader

        def load(self) -> "ProtostarProjectSection":
            return ProtostarProjectSection.load(self._protostar_toml_reader)

    libs_path: Path

    @staticmethod
    def get_section_name() -> str:
        return "project"

    @classmethod
    def get_default(cls) -> "ProtostarProjectSection":
        return cls(libs_path=Path("lib"))

    @classmethod
    def load(cls, protostar_toml: ProtostarTOMLReader) -> "ProtostarProjectSection":
        section_dict = protostar_toml.get_section(cls.get_section_name())
        if section_dict is None:
            raise InvalidProtostarTOMLException(cls.get_section_name())
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarProjectSection":
        return cls(
            libs_path=cls._load_path_from_raw_dict(raw_dict, attribute_name="libs_path")
        )

    def to_dict(self) -> "ProtostarTOMLSection.ParsedProtostarTOML":
        result: "ProtostarTOMLSection.ParsedProtostarTOML" = {}

        result["libs_path"] = str(self.libs_path)

        return result
