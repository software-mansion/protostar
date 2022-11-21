from dataclasses import dataclass
from pathlib import Path

from protostar.self import ContractName


@dataclass(eq=True, frozen=True, unsafe_hash=True)
class ContractSourceIdentifier:
    contract_name: ContractName
    contract_paths: list[Path]
