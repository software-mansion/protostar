from dataclasses import dataclass
from typing import Optional

from protostar.scripting.typing import Fee


@dataclass
class DeclaredContract:
    class_hash: int


def declare(
    contract: str,
    *,
    wait_for_acceptance: Optional[bool] = None,
    max_fee: Optional[Fee] = None,
) -> DeclaredContract:
    raise NotImplementedError
