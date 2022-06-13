from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_section import ProtostarTOMLSection


@dataclass
class ProtostarContractsSection(ProtostarTOMLSection):
    contract_name_to_paths: Dict[str, List[Path]]

    @staticmethod
    def get_section_name() -> str:
        return "contracts"

    @classmethod
    def from_protostar_toml_reader(
        cls, protostar_toml_reader: ProtostarTOMLReader
    ) -> "ProtostarContractsSection":
        section_dict = protostar_toml_reader.get_section(cls.get_section_name())
        if section_dict is None:
            return cls.from_dict({})
        return cls.from_dict(section_dict)

    @classmethod
    def from_dict(cls, raw_dict: Dict[str, Any]) -> "ProtostarContractsSection":
        contract_name_to_paths: Dict[str, List[Path]] = {}
        for contract_name, str_paths in raw_dict.items():
            contract_name_to_paths[contract_name] = [
                Path(str_path) for str_path in str_paths
            ]
        return cls(contract_name_to_paths=contract_name_to_paths)

    def to_dict(self) -> "ProtostarTOMLSection.TOMLCompatibleDict":
        result: "ProtostarTOMLSection.TOMLCompatibleDict" = {}

        for contract_name, paths in self.contract_name_to_paths.items():
            result[contract_name] = [str(path) for path in paths]

        return result
