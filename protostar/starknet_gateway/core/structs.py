from dataclasses import dataclass

from protostar.starknet import Address, CairoData

from .types import Wei


@dataclass
class PreparedInvokeTransaction:
    account_address: Address
    account_execute_calldata: CairoData
    max_fee: Wei
    nonce: int
    signature: list[int]
