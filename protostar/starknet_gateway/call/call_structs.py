from dataclasses import dataclass
from typing import Union

from protostar.starknet import Address, Selector

CairoCalldata = list[int]
PythonCalldata = dict
Calldata = Union[CairoCalldata, PythonCalldata]


@dataclass
class CallInput:
    address: Address
    selector: Selector
    inputs: Calldata


@dataclass
class CallOutput:
    data: list[int]


@dataclass
class CallClientPayload:
    address: Address
    selector: Selector
    cairo_calldata: CairoCalldata


@dataclass
class CallClientResponse:
    data: CairoCalldata
