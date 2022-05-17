from pathlib import Path
from typing import List, Optional

from protostar.cli.command import Command
from protostar.commands.deploy.deploy_contract import deploy_contract
from protostar.commands.deploy.network_config import NetworkConfig
from protostar.utils.config.project import Project


class DeployCommand(Command):
    def __init__(self, project: Project, build_output_path: Path) -> None:
        self._project = project
        self._build_output_path = build_output_path

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "Deploys contracts."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="contract",
                description='A name of the contract defined in protostar.toml::["protostar.contracts"]',
                type="str",
            ),
            Command.Argument(
                name="inputs",
                description="The inputs to the constructor",
                type="str",
                is_array=True,
            ),
            Command.Argument(
                name="network",
                description="A name of the network defined in protostar.toml",
                type="str",
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
        ]

    async def run(self, args):
        return await self.deploy(
            contract_name=args.contract,
            network=args.network,
            inputs=args.inputs,
            token=args.token,
            salt=args.salt,
        )

    # pylint: disable=too-many-arguments
    async def deploy(
        self,
        contract_name: str,
        network: str,
        inputs: Optional[List[str]] = None,
        token: Optional[str] = None,
        salt: Optional[str] = None,
    ):
        with open(
            self._build_output_path / f"{contract_name}.json",
            mode="r",
            encoding="utf-8",
        ) as compiled_contract_file:
            network_config = NetworkConfig.from_config_file(network, self._project)

            await deploy_contract(
                gateway_url=network_config.gateway_url,
                compiled_contract_file=compiled_contract_file,
                constructor_args=inputs,
                salt=salt,
                token=token,
            )
