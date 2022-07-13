from pathlib import Path
from typing import List, Optional

from protostar.commands.deploy.deploy_command import CompilationOutputNotFoundException
from protostar.deployer.network_config import NetworkConfig
from protostar.deployer.starkware.starknet_cli import deploy


class InvalidNetworkConfigurationException(BaseException):
    pass


class Deployer:
    def __init__(self, project_root_path: Path) -> None:
        self._project_root_path = project_root_path

    @staticmethod
    def build_network_config(
        gateway_url: Optional[str] = None,
        network: Optional[str] = None,
    ) -> NetworkConfig:
        network_config: Optional[NetworkConfig] = None

        if network:
            network_config = NetworkConfig.from_starknet_network_name(network)
        if gateway_url:
            network_config = NetworkConfig(gateway_url=gateway_url)

        if network_config is None:
            raise InvalidNetworkConfigurationException()

        return network_config

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        compiled_contract_path: Path,
        network_config: NetworkConfig,
        inputs: Optional[List[str]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ):

        compilation_output_filepath = self._project_root_path / compiled_contract_path

        try:
            with open(
                self._project_root_path / compilation_output_filepath,
                mode="r",
                encoding="utf-8",
            ) as compiled_contract_file:
                return await deploy(
                    gateway_url=network_config.gateway_url,
                    compiled_contract_file=compiled_contract_file,
                    constructor_args=inputs,
                    salt=salt,
                    token=token,
                )

        except FileNotFoundError as err:
            raise CompilationOutputNotFoundException(
                (
                    f"Couldn't find `{compilation_output_filepath}`\n"
                    "Did you run `protostar build` before running this command?"
                )
            ) from err
