from dataclasses import dataclass
from typing import Optional, Union

from protostar.starknet import Address, Selector
from protostar.starknet_gateway.types import Fee

DeployCallName = str
MulticallInputCalldata = list[Union[int, DeployCallName]]


@dataclass(frozen=True)
class InvokeCall:
    address: Union[DeployCallName, Address]
    selector: Selector
    calldata: MulticallInputCalldata


@dataclass(frozen=True)
class DeployCall:
    class_hash: int
    calldata: MulticallInputCalldata
    name: Optional[DeployCallName] = None


Call = Union[DeployCall, InvokeCall]


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
    calls: list[Call]
    max_fee: Fee


@dataclass(frozen=True)
class MulticallOutput:
    transaction_hash: int
    deployed_contract_addresses: dict[DeployCallName, Address]
