from typing import Protocol

from .invoke_structs import (
    UnsignedInvokeTransaction,
    SignedInvokeTransaction,
    InvokeClientResponse,
)


class InvokeAccountManagerProtocol(Protocol):
    async def sign_invoke_transaction(
        self,
        unsigned_tx: UnsignedInvokeTransaction,
    ) -> SignedInvokeTransaction:
        ...


class InvokeClientProtocol(Protocol):
    async def send_invoke_transaction(
        self, signed_tx: SignedInvokeTransaction
    ) -> InvokeClientResponse:
        ...

    async def wait_for_acceptance(self, tx_hash: int) -> None:
        ...
