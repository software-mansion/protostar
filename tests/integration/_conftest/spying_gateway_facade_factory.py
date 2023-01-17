from pathlib import Path
from typing import Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.starknet_gateway import GatewayFacade, GatewayFacadeFactory

from .gateway_client_tx_interceptor import GatewayClientTxInterceptor
from .transaction_registry import TransactionRegistry


class SpyingGatewayFacadeFactory(GatewayFacadeFactory):
    def __init__(
        self,
        project_root_path: Path,
        transaction_registry: TransactionRegistry,
    ) -> None:
        super().__init__(project_root_path)
        self.recent_gateway_client: Optional[GatewayClientTxInterceptor] = None
        self._transaction_registry = transaction_registry

    def create(self, gateway_client: GatewayClient):
        gateway_client_tx_interceptor = GatewayClientTxInterceptor(
            # pylint: disable=protected-access
            net=gateway_client._net,
            transaction_registry=self._transaction_registry,
        )
        self.recent_gateway_client = gateway_client_tx_interceptor
        return GatewayFacade(
            project_root_path=self._project_root_path,
            gateway_client=gateway_client_tx_interceptor,
        )
