from dataclasses import dataclass
from typing import Optional, Union

from protostar.starknet import Address


@dataclass(frozen=True)
class CallBase:
    calldata: list[int]


DeployCallName = str


@dataclass(frozen=True)
class InvokeCall(CallBase):
    address: Union[DeployCallName, Address]
    function_name: str


@dataclass(frozen=True)
class DeployCall(CallBase):
    class_hash: int
    name: Optional[DeployCallName] = None


@dataclass(frozen=True)
class MulticallInput:
    calls: list[CallBase]
