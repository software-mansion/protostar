from pathlib import Path

from starknet_py.net.gateway_client import GatewayClient

from protostar.compiler import CompiledContractReader
from .gateway_facade import GatewayFacade


class GatewayFacadeFactory:
    def __init__(
        self,
        project_root_path: Path,
        compiled_contract_reader: CompiledContractReader,
    ) -> None:
        self._project_root_path = project_root_path
        self._compiled_contract_reader = compiled_contract_reader

    def create(self, gateway_client: GatewayClient):
        return GatewayFacade(
            project_root_path=self._project_root_path,
            compiled_contract_reader=self._compiled_contract_reader,
            gateway_client=gateway_client,
        )
