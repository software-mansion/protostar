from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from protostar.protostar_toml._protostar_toml_section import ProtostarTOMLSection
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)


@dataclass
class ProtostarProject(ProtostarTOMLSection):
    libs_path: Path

    @staticmethod
    def get_name() -> str:
        return "project"

    @classmethod
    def from_protostar_toml(
        cls, protostar_toml: ProtostarTOMLReader
    ) -> "ProtostarProject":
        section_dict = protostar_toml.get_section(cls.get_name())
        if section_dict is None:
            raise InvalidProtostarTOMLException(cls.get_name())
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarProject":
        return cls(libs_path=Path(raw_dict["libs_path"]))

    def to_dict(self) -> "ProtostarTOMLSection.Dict":
        result: "ProtostarTOMLSection.Dict" = {}

        result["libs_path"] = str(self.libs_path)

        return result
