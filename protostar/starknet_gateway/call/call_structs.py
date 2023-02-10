from dataclasses import dataclass
from typing import Optional

from protostar.starknet import (
    Address,
    Selector,
    ContractAbi,
    PythonData,
    CairoOrPythonData,
    CairoData,
)


@dataclass
class CallInput:
    address: Address
    selector: Selector
    inputs: Optional[CairoOrPythonData]
    contract_abi: Optional[ContractAbi]


@dataclass
class CallOutput:
    cairo_data: CairoData
    human_data: Optional[PythonData]
