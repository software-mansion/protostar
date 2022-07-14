from logging import Logger
from typing import List, Optional

from protostar.cli.command import Command
from protostar.deployer import Deployer
from protostar.deployer.deployer import InvalidNetworkConfigurationException
from protostar.deployer.network_config import NetworkConfig
from protostar.protostar_exception import ProtostarException


class CompilationOutputNotFoundException(ProtostarException):
    pass


class DeployCommand(Command):

    gateway_url_arg = Command.Argument(
        name="gateway-url",
        description="The URL of a StarkNet gateway. It is required unless `--network` is provided.",
        type="str",
    )

    network_arg = Command.Argument(
        name="network",
        short_name="n",
        description=(
            "\n".join(
                [
                    "The name of the StarkNet network.",
                    "It is required unless `--gateway-url` is provided.",
                    "",
                    "Supported StarkNet networks:",
                ]
                + [f"- `{n}`" for n in NetworkConfig.get_starknet_networks()]
            )
        ),
        type="str",
    )

    def __init__(self, deployer: Deployer, logger: Logger) -> None:
        self._deployer = deployer
        self._logger = logger

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
        return "protostar deploy ./build/main.json --network alpha-goerli"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="contract",
                description="The path to the compiled contract.",
                type="path",
                is_required=True,
                is_positional=True,
            ),
            Command.Argument(
                name="inputs",
                short_name="i",
                description=(
                    "The inputs to the constructor. "
                    "Calldata arguments may be of any type that does not contain pointers.\n"
                    # pylint: disable=line-too-long
                    "[Read more about representing Cairo data types in the CLI.](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata)"
                ),
                type="str",
                is_array=True,
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
        try:
            network_config = self._deployer.build_network_config(
                network=args.network, gateway_url=args.gateway_url
            )
        except InvalidNetworkConfigurationException as err:
            raise ProtostarException(
                f"Argument `{DeployCommand.gateway_url_arg.name}` or `{DeployCommand.network_arg.name}` is required"
            ) from err

        response = await self._deployer.deploy(
            compiled_contract_path=args.contract,
            network_config=network_config,
            inputs=args.inputs,
            token=args.token,
            salt=args.salt,
        )

        explorer_url = network_config.get_contract_explorer_url(response.address)
        explorer_url_msg_lines: List[str] = []

        if explorer_url:
            explorer_url_msg_lines = ["", explorer_url]

        response.log(self._logger, extra_msg=explorer_url_msg_lines)

        return response
