from dataclasses import dataclass
from typing import Optional

from protostar.starknet_gateway.core import Fee
from protostar.starknet import (
    Calldata,
    Address,
    Selector,
    AbiType,
    CairoDataRepresentation,
)


@dataclass
class InvokeInput:
    address: Address
    selector: Selector
    calldata: Optional[Calldata]
    max_fee: Fee
    abi: Optional[AbiType]


@dataclass
class UnsignedInvokeTransaction:
    address: Address
    selector: Selector
    calldata: CairoDataRepresentation
    max_fee: Fee


@dataclass
class InvokeOutput:
    transaction_hash: int
