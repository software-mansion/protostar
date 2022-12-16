from typing import Protocol

from protostar.starknet_gateway.core import (
    PayloadToAccountExecuteInvokeTx,
    AccountManagerProtocol,
)

from .invoke_structs import UnsignedInvokeTransaction


class InvokeClientProtocol(Protocol):
    async def wait_for_acceptance(self, tx_hash: int) -> None:
        ...


class InvokeAccountManagerProtocol(AccountManagerProtocol, Protocol):
    async def prepare_execute_payload_from_unsigned_invoke_tx(
        self,
        unsigned_tx: UnsignedInvokeTransaction,
    ) -> PayloadToAccountExecuteInvokeTx:
        ...
