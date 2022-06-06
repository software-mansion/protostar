from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection


@dataclass
class ProtostarContractsSection(ProtostarTOMLSection):
    contract_dict: Dict[str, List[Path]]

    @staticmethod
    def get_section_name() -> str:
        return "contracts"

    @classmethod
    def from_protostar_toml(
        cls, protostar_toml: ProtostarTOMLReader
    ) -> "ProtostarContractsSection":
        section_dict = protostar_toml.get_section(cls.get_section_name())
        if section_dict is None:
            raise InvalidProtostarTOMLException(cls.get_section_name())
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(
        cls, raw_dict: Optional[Dict[str, Any]]
    ) -> "ProtostarContractsSection":
        if not raw_dict:
            return cls(contract_dict={})

        contract_dict: Dict[str, List[Path]] = {}
        for contract_name, str_paths in raw_dict.items():
            contract_dict[contract_name] = [Path(str_path) for str_path in str_paths]
        return cls(contract_dict=contract_dict)

    def to_dict(self) -> "ProtostarTOMLSection.Dict":
        result: "ProtostarTOMLSection.Dict" = {}

        for contract_name, path in self.contract_dict:
            result[contract_name] = str(path)

        return result
