from typing import Protocol

from .invoke_structs import (
    UnsignedInvokeTransaction,
    SignedInvokeTransaction,
    ClientResponse,
)


class AccountManagerProtocol(Protocol):
    async def sign_invoke_transaction(
        self,
        unsigned_invoke_transaction: UnsignedInvokeTransaction,
    ) -> SignedInvokeTransaction:
        ...


class ClientProtocol(Protocol):
    async def send_invoke_transaction(
        self, signed_invoke_transaction: SignedInvokeTransaction
    ) -> ClientResponse:
        ...
