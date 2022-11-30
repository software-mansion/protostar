from protostar.architecture import UseCase

from .multicall_input import MulticallInput
from .multicall_output import MulticallOutput
from .multicall_protocols import (
    MulticallClientProtocol,
    UnsignedMulticallTransaction,
    AccountManagerProtocol,
)
from .call_resolver import CallResolver


class MulticallUseCase(UseCase[MulticallInput, MulticallOutput]):
    def __init__(
        self,
        client: MulticallClientProtocol,
        account_manager: AccountManagerProtocol,
        call_resolver: CallResolver,
    ) -> None:
        super().__init__()
        self._account_manager = account_manager
        self._client = client
        self._call_resolver = call_resolver

    async def execute(self, data: MulticallInput):
        resolved_calls = await self._call_resolver.resolve(data.calls)
        unsigned_tx = UnsignedMulticallTransaction(calls=resolved_calls)
        signed_transaction = await self._account_manager.sign_invoke_transaction(
            unsigned_tx
        )
        return await self._client.send_multicall_transaction(signed_transaction)
