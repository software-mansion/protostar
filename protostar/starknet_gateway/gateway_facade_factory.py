from pathlib import Path

from starknet_py.net.gateway_client import GatewayClient

from .gateway_facade import GatewayFacade


class GatewayFacadeFactory:
    def __init__(
        self,
        project_root_path: Path,
    ) -> None:
        self._project_root_path = project_root_path

    def create(self, gateway_client: GatewayClient):
        return GatewayFacade(
            project_root_path=self._project_root_path,
            gateway_client=gateway_client,
        )
