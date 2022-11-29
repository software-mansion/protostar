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
class InvokeSignedTransaction:
    contract_address: Address
    # selector: Selector
    calldata: list[int]
    max_fee: int
    nonce: int
    signature: list[int]


class AccountManagerProtocol(Protocol):
    @abstractmethod
    def get_account_address(self) -> Address:
        ...

    @abstractmethod
    async def sign_invoke_transaction(
        self, unsigned_transaction: UnsignedMulticallTransaction
    ) -> InvokeSignedTransaction:
        ...


class MulticallClientProtocol(Protocol):
    @abstractmethod
    async def send_multicall_transaction(
        self, transaction: InvokeSignedTransaction
    ) -> MulticallOutput:
        ...
