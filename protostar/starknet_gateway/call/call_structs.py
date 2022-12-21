from dataclasses import dataclass
from typing import Optional

from protostar.starknet import (
    Address,
    Selector,
    AbiType,
    PythonData,
    CairoOrPythonData,
    CairoData,
)


@dataclass
class CallInput:
    address: Address
    selector: Selector
    inputs: Optional[CairoOrPythonData]
    abi: Optional[AbiType]


@dataclass
class CallOutput:
    cairo_data: CairoData
    human_data: Optional[PythonData]
