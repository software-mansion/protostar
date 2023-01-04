from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DeployedContract:
    contract_address: int


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int
    salt: int


@dataclass
class DeclaredContract:
    class_hash: int
