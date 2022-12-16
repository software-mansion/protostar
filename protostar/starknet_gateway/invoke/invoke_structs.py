from dataclasses import dataclass
from typing import Optional

from protostar.starknet_gateway.core import Fee
from protostar.starknet import (
    Calldata,
    Address,
    Selector,
    Wei,
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
class SignedInvokeTransaction:
    account_address: Address
    account_execute_calldata: CairoDataRepresentation
    max_fee: Wei
    nonce: Optional[int]
    signature: list[int]


@dataclass
class InvokeClientResponse:
    transaction_hash: int


@dataclass
class InvokeOutput:
    transaction_hash: int
