from dataclasses import dataclass
from typing import Optional

from protostar.starknet import (
    Address,
    Selector,
    ContractAbiService,
    PythonData,
    CairoOrPythonData,
    CairoData,
)


@dataclass
class CallInput:
    address: Address
    selector: Selector
    inputs: Optional[CairoOrPythonData]
    contract_abi_service: Optional[ContractAbiService]


@dataclass
class CallOutput:
    cairo_data: CairoData
    human_data: Optional[PythonData]
