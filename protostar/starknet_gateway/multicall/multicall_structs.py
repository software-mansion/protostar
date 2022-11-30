from dataclasses import dataclass
from typing import Optional, Union

from protostar.starknet import Address, Selector

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


@dataclass
class ResolvedCall:
    address: Address
    selector: Selector
    calldata: list[int]


@dataclass
class UnsignedMulticallTransaction:
    calls: list[ResolvedCall]


@dataclass
class SignedMulticallTransaction:
    contract_address: Address
    calldata: list[int]
    max_fee: int
    nonce: int
    signature: list[int]


@dataclass
class MulticallClientResponse:
    transaction_hash: int


@dataclass(frozen=True)
class MulticallInput:
    calls: list[CallBase]


@dataclass(frozen=True)
class MulticallOutput:
    transaction_hash: int
    deployed_contract_addresses: dict[DeployCallName, Address]
