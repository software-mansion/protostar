from dataclasses import dataclass

from protostar.starknet import Address


@dataclass
class SuccessfulDeployResponse:
    code: str
    address: Address
    transaction_hash: int


@dataclass
class SuccessfulDeclareResponse:
    code: str
    class_hash: int
    transaction_hash: int


@dataclass
class SuccessfulInvokeResponse:
    transaction_hash: int


@dataclass
class SuccessfulDeployAccountResponse:
    address: Address
    transaction_hash: int
    code: str
