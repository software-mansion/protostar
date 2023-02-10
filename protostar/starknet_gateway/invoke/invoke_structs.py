from dataclasses import dataclass
from typing import Optional

from protostar.starknet import ContractAbi, CairoOrPythonData, Address, Selector
from protostar.starknet_gateway.core import Fee


@dataclass
class InvokeInput:
    address: Address
    selector: Selector
    calldata: Optional[CairoOrPythonData]
    max_fee: Fee
    contract_abi: Optional[ContractAbi]


@dataclass
class InvokeOutput:
    transaction_hash: int
