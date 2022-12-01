from .call_resolver import CallResolver
from .multicall_structs import MulticallInput, MulticallOutput
from .multicall_protocols import (
    MulticallClientProtocol,
    UnsignedMulticallTransaction,
    MulticallAccountManagerProtocol,
)


class MulticallUseCase:
    def __init__(
        self,
        client: MulticallClientProtocol,
        account_manager: MulticallAccountManagerProtocol,
    ) -> None:
        super().__init__()
        self._account_manager = account_manager
        self._client = client
        self._call_resolver = CallResolver()

    async def execute(self, data: MulticallInput) -> MulticallOutput:
        resolved_calls = await self._call_resolver.resolve(data.calls)
        unsigned_tx = UnsignedMulticallTransaction(calls=resolved_calls)
        signed_transaction = await self._account_manager.sign_multicall_transaction(
            unsigned_tx
        )
        response = await self._client.send_multicall_transaction(signed_transaction)
        return MulticallOutput(
            transaction_hash=response.transaction_hash,
            deployed_contract_addresses=self._call_resolver.get_deploy_call_name_to_address(),
        )
