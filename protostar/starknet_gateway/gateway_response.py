from dataclasses import dataclass

from protostar.starknet import Address, AccountAddress


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
    address: AccountAddress
    transaction_hash: int
    code: str
