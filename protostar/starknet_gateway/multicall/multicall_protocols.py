from abc import abstractmethod
from dataclasses import dataclass

from typing_extensions import Protocol

from protostar.starknet import Address, Selector

from .multicall_output import MulticallOutput


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


class MulticallAccountManagerProtocol(Protocol):
    @abstractmethod
    def get_account_address(self) -> Address:
        ...

    @abstractmethod
    async def sign_multicall_transaction(
        self, unsigned_transaction: UnsignedMulticallTransaction
    ) -> SignedMulticallTransaction:
        ...


class MulticallClientProtocol(Protocol):
    @abstractmethod
    async def send_multicall_transaction(
        self, transaction: SignedMulticallTransaction
    ) -> MulticallOutput:
        ...
