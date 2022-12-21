from dataclasses import dataclass
from typing import Optional

from protostar.starknet import Address, CairoDataRepresentation

from .types import Wei


@dataclass
class PreparedInvokeTransaction:
    account_address: Address
    account_execute_calldata: CairoDataRepresentation
    max_fee: Wei
    nonce: Optional[int]
    signature: list[int]
