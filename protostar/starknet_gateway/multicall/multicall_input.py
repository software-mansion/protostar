from dataclasses import dataclass
from typing import Literal, Union

from protostar.starknet import Address


@dataclass(frozen=True)
class CallBase:
    calldata: list[int]


@dataclass(frozen=True)
class InvokeCall(CallBase):
    address: Union[Literal["FROM_DEPLOY"], Address]
    function_name: str


@dataclass(frozen=True)
class DeployCall(CallBase):
    compiled_contract: str


@dataclass(frozen=True)
class MulticallInput:
    calls: list[CallBase]
