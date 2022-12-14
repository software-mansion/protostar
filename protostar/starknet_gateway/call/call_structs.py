from dataclasses import dataclass
from typing import Optional, Union

from protostar.starknet import Address, Selector, AbiType

CairoDataRepresentation = list[int]
HumanDataRepresentation = dict
Calldata = Union[CairoDataRepresentation, HumanDataRepresentation]


@dataclass
class CallInput:
    address: Address
    selector: Selector
    inputs: Calldata
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
