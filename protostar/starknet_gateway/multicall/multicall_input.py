from dataclasses import dataclass
from typing import Literal, Union

from protostar.starknet import Address

from ..gateway_facade import Fee


@dataclass(frozen=True)
class CallBase:
    contract_source: str
    calldata: list[int]
    max_fee: Fee


@dataclass(frozen=True)
class InvokeCall(CallBase):
    address: Union[Literal["FROM_DEPLOY"], Address]
    function_name: str


@dataclass(frozen=True)
class DeployCall(CallBase):
    pass


@dataclass(frozen=True)
class MulticallInput:
    calls: list[CallBase]
