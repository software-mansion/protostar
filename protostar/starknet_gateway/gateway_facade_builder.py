from pathlib import Path
from typing import Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.compiler import CompiledContractReader

from .gateway_facade import GatewayFacade


class GatewayFacadeBuilder:
    def __init__(
        self,
        project_root_path: Path,
        compiled_contract_reader: CompiledContractReader,
    ) -> None:
        self._project_root_path = project_root_path
        self._compiled_contract_reader = compiled_contract_reader
        self._gateway_client: Optional[GatewayClient] = None

    def set_gateway_client(self, gateway_client: GatewayClient) -> None:
        self._gateway_client = gateway_client

    def build(self):
        assert self._gateway_client is not None
        return GatewayFacade(
            project_root_path=self._project_root_path,
            gateway_client=self._gateway_client,
            compiled_contract_reader=self._compiled_contract_reader,
        )
