from dataclasses import dataclass
from typing import Optional, Union

from protostar.starknet import Address, Selector
from protostar.starknet_gateway.gateway_facade import Fee

DeployCallName = str

MulticallInputCalldata = list[Union[int, DeployCallName]]


@dataclass(frozen=True)
class CallBase:
    calldata: MulticallInputCalldata


@dataclass(frozen=True)
class InvokeCall(CallBase):
    address: Union[DeployCallName, Address]
    selector: Selector


@dataclass(frozen=True)
class DeployCall(CallBase):
    class_hash: int
    name: Optional[DeployCallName] = None


@dataclass(frozen=True)
class ResolvedCall:
    address: Address
    selector: Selector
    calldata: list[int]


@dataclass(frozen=True)
class UnsignedMulticallTransaction:
    calls: list[ResolvedCall]
    max_fee: Fee


@dataclass(frozen=True)
class SignedMulticallTransaction:
    contract_address: Address
    calldata: list[int]
    max_fee: int
    nonce: Optional[int]
    signature: list[int]


@dataclass(frozen=True)
class MulticallClientResponse:
    transaction_hash: int


@dataclass(frozen=True)
class MulticallInput:
    calls: list[CallBase]
    max_fee: Fee


@dataclass(frozen=True)
class MulticallOutput:
    transaction_hash: int
    deployed_contract_addresses: dict[DeployCallName, Address]
