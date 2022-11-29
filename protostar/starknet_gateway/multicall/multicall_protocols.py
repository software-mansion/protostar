from abc import abstractmethod
from dataclasses import dataclass

from typing_extensions import Self, Protocol

from protostar.starknet import Address, Selector

from .multicall_output import MulticallOutput


@dataclass
class InvokeUnsignedTransaction:
    contract_address: Address
    selector: Selector
    calldata: list[int]


@dataclass
class InvokeSignedTransaction(InvokeUnsignedTransaction):
    @classmethod
    def from_unsigned(
        cls,
        unsigned_invoke_transaction: InvokeUnsignedTransaction,
        max_fee: int,
        nonce: int,
        signature: list[int],
    ) -> Self:
        return InvokeSignedTransaction(
            contract_address=unsigned_invoke_transaction.contract_address,
            calldata=unsigned_invoke_transaction.calldata,
            selector=unsigned_invoke_transaction.selector,
            max_fee=max_fee,
            nonce=nonce,
            signature=signature,
        )

    max_fee: int
    nonce: int
    signature: list[int]


@dataclass
class ResolvedCall:
    address: Address
    selector: Selector
    calldata: list[int]


class AccountManagerProtocol(Protocol):
    @abstractmethod
    def get_account_address(self) -> Address:
        ...

    @abstractmethod
    async def sign_invoke_transaction(
        self, unsigned_transaction: InvokeUnsignedTransaction
    ) -> InvokeSignedTransaction:
        ...


class MulticallClientProtocol(Protocol):
    @abstractmethod
    async def send_multicall_transaction(
        self, transaction: InvokeSignedTransaction
    ) -> MulticallOutput:
        ...
