from dataclasses import dataclass


@dataclass
class SuccessfulDeployResponse:
    code: str
    address: int
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
    address: int
    transaction_hash: int
    code: str
