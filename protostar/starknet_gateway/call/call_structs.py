from dataclasses import dataclass
from typing import Optional

from protostar.starknet import (
    Address,
    Selector,
    AbiType,
    HumanDataRepresentation,
    Calldata,
    CairoDataRepresentation,
)


@dataclass
class CallInput:
    address: Address
    selector: Selector
    inputs: Optional[Calldata]
    abi: Optional[AbiType]


@dataclass
class CallPayload:
    address: Address
    selector: Selector
    cairo_calldata: CairoDataRepresentation


@dataclass
class CallResponse:
    cairo_data: CairoDataRepresentation


@dataclass
class CallOutput:
    cairo_data: CairoDataRepresentation
    human_data: Optional[HumanDataRepresentation]
