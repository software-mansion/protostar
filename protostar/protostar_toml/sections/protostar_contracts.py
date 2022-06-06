from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from protostar.protostar_toml.sections._protostar_toml_section import (
    ProtostarTOMLSection,
)


@dataclass
class ProtostarContracts(ProtostarTOMLSection):
    contract_dict: Dict[str, List[Path]]

    @staticmethod
    def get_name() -> str:
        return "contracts"

    @classmethod
    def from_dict(cls, raw_dict: Optional[Dict[str, Any]]) -> "ProtostarContracts":
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
