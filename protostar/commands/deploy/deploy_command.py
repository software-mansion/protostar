from pathlib import Path
from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.deploy.deploy_contract import (
    SuccessfulGatewayResponseFacade,
    deploy_contract,
)
from protostar.commands.deploy.network_config import NetworkConfig
from protostar.commands.shared_args import output_shared_argument
from protostar.utils.config.project import Project


class DeployCommand(Command):
    def __init__(self, project: Project) -> None:
        self._project = project

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "\n".join(
            [
                "Deploys contracts. Before running this command you need to configure networks in the `protostar.toml`",
                "",
                "Network configuration examples:",
                "",
                "[protostar.network.devnet]",
                'gateway_url = "http://127.0.0.1:5050/"',
                "",
                "[protostar.network.testnet]",
                'network = "alpha-goerli"',
                "",
                "[protostar.network.mainnet]",
                'network = "alpha-mainnet"',
                "",
            ]
        )

    @property
    def example(self) -> Optional[str]:
        return "protostar deploy -c main -n testnet"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="contract",
                description='A name of the contract defined in protostar.toml::["protostar.contracts"]',
                type="str",
                is_required=True,
                is_positional=True,
            ),
            Command.Argument(
                name="inputs",
                short_name="i",
                description="The inputs to the constructor",
                type="str",
                is_array=True,
            ),
            Command.Argument(
                name="network",
                short_name="n",
                description="A name of the network defined in protostar.toml",
                type="str",
                is_required=True,
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
            output_shared_argument,
        ]

    async def run(self, args):
        return await self.deploy(
            contract_name=args.contract,
            network=args.network,
            output_dir=args.output,
            inputs=args.inputs,
            token=args.token,
            salt=args.salt,
        )

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        contract_name: str,
        network: str,
        output_dir: Path,
        inputs: Optional[List[str]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ) -> SuccessfulGatewayResponseFacade:
        with open(
            self._project.project_root / output_dir / f"{contract_name}.json",
            mode="r",
            encoding="utf-8",
        ) as compiled_contract_file:
            network_config = NetworkConfig.from_config_file(network, self._project)

            return await deploy_contract(
                gateway_url=network_config.gateway_url,
                compiled_contract_file=compiled_contract_file,
                constructor_args=inputs,
                salt=salt,
                token=token,
            )
