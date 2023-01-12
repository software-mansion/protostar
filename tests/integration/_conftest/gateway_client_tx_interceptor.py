from typing import Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.client_models import StarknetTransaction
from starknet_py.net.networks import Network

from .transaction_registry import TransactionRegistry


class GatewayClientTxInterceptor(GatewayClient):
    def __init__(self, net: Network, transaction_registry: TransactionRegistry):
        super().__init__(net, session=None)
        self.intercepted_txs: list[StarknetTransaction] = []
        self._transaction_registry = transaction_registry

    async def _add_transaction(
        self,
        tx: StarknetTransaction,
        token: Optional[str] = None,
    ) -> dict:
        self.intercepted_txs.append(tx)
        self._transaction_registry.register(tx)
        return await super()._add_transaction(tx, token)
