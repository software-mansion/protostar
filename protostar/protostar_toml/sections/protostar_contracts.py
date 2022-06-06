from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ProtostarContracts:
    contract_dict: Dict[str, List[Path]]

    @classmethod
    def from_dict(cls, raw_dict: Optional[Dict[str, Any]]) -> "ProtostarContracts":
        if not raw_dict:
            return cls(contract_dict={})

        contract_dict: Dict[str, List[Path]] = {}
        for contract_name, str_paths in raw_dict.items():
            contract_dict[contract_name] = [Path(str_path) for str_path in str_paths]
        return cls(contract_dict=contract_dict)
