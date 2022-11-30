from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput
from .multicall_protocols import (
    MulticallClientProtocol,
    UnsignedMulticallTransaction,
    MulticallAccountManagerProtocol,
)
from .call_resolver import CallResolver


class MulticallUseCase:
    def __init__(
        self,
        client: MulticallClientProtocol,
        account_manager: MulticallAccountManagerProtocol,
        call_resolver: CallResolver,
    ) -> None:
        super().__init__()
        self._account_manager = account_manager
        self._client = client
        self._call_resolver = call_resolver

    async def execute(self, data: MulticallInput) -> MulticallOutput:
        resolved_calls = await self._call_resolver.resolve(data.calls)
        unsigned_tx = UnsignedMulticallTransaction(calls=resolved_calls)
        signed_transaction = await self._account_manager.sign_multicall_transaction(
            unsigned_tx
        )
        return await self._client.send_multicall_transaction(signed_transaction)
