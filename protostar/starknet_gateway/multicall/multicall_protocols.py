from abc import abstractmethod

from typing_extensions import Protocol

from protostar.starknet import Address

from .multicall_structs import (
    SignedMulticallTransaction,
    MulticallClientResponse,
    UnsignedMulticallTransaction,
)


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
    ) -> MulticallClientResponse:
        ...
