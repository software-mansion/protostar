from pathlib import Path
from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.deploy.network_config import NetworkConfig
from protostar.commands.deploy.starkware.starknet_cli import (
    SuccessfulGatewayResponse,
    deploy,
)
from protostar.protostar_exception import ProtostarException
from protostar.utils.config.project import Project


class DeployCommand(Command):
    gateway_url_arg = Command.Argument(
        name="gateway_url",
        description="The URL of a StarkNet gateway.",
        type="str",
    )

    network_arg = Command.Argument(
        name="network",
        description="The name of the StarkNet network.",
        type="str",
    )

    def __init__(self, project: Project) -> None:
        self._project = project

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "\n".join(
            [
                "Deploys contracts.",
            ]
        )

    @property
    def example(self) -> Optional[str]:
        return "protostar deploy main -n testnet"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="contract",
                description='A name of the contract defined in protostar.toml::["protostar.contracts"].',
                type="str",
                is_required=True,
                is_positional=True,
            ),
            Command.Argument(
                name="inputs",
                short_name="i",
                description="The inputs to the constructor.",
                type="str",
                is_array=True,
            ),
            Command.Argument(
                name="build-output",
                description="An output directory used to put the compiled contracts in.",
                type="path",
                default="build",
            ),
            Command.Argument(
                name="token",
                description="Used for deploying contracts in Alpha MainNet.",
                type="str",
            ),
            Command.Argument(
                name="salt",
                description=(
                    "An optional salt controlling where the contract will be deployed. "
                    "The contract deployment address is determined by the hash "
                    "of contract, salt and caller. "
                    "If the salt is not supplied, the contract will be deployed with a random salt."
                ),
                type="str",
            ),
            DeployCommand.gateway_url_arg,
            DeployCommand.network_arg,
        ]

    async def run(self, args):
        return await self.deploy(
            contract_name=args.contract,
            network=args.network,
            build_output_dir=args.build_output,
            inputs=args.inputs,
            token=args.token,
            salt=args.salt,
        )

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        contract_name: str,
        build_output_dir: Path,
        inputs: Optional[List[str]] = None,
        network: Optional[str] = None,
        gateway_url: Optional[str] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ) -> SuccessfulGatewayResponse:
        with open(
            self._project.project_root / build_output_dir / f"{contract_name}.json",
            mode="r",
            encoding="utf-8",
        ) as compiled_contract_file:

            network_config = self._build_network_config(
                gateway_url=gateway_url, network=network
            )

            return await deploy(
                gateway_url=network_config.gateway_url,
                compiled_contract_file=compiled_contract_file,
                constructor_args=inputs,
                salt=salt,
                token=token,
            )

    # pylint: disable=no-self-use
    def _build_network_config(
        self,
        gateway_url: Optional[str] = None,
        network: Optional[str] = None,
    ) -> NetworkConfig:
        network_config: Optional[NetworkConfig] = None

        if network:
            network_config = NetworkConfig.from_starknet_network_name(network)
        if gateway_url:
            network_config = NetworkConfig(gateway_url=gateway_url)

        if network_config is None:
            raise ProtostarException(
                f"Argument `{DeployCommand.gateway_url_arg.name}` or `{DeployCommand.network_arg.name}` is required"
            )

        return network_config
