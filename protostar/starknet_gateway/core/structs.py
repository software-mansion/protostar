from dataclasses import dataclass
from typing import Optional

from protostar.starknet import Address, CairoData

from .types import Wei


@dataclass
class PreparedInvokeTransaction:
    account_address: Address
    account_execute_calldata: CairoData
    max_fee: Wei
    nonce: Optional[int]
    signature: list[int]
