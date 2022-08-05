from logging import Logger
from typing import List, Optional

from protostar.cli.command import Command
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import GatewayFacade
from protostar.starknet_gateway.network_config import NetworkConfig


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

    wait_for_acceptance_arg = Command.Argument(
        name="wait-for-acceptance",
        description="Waits for transaction to be accepted on chain.",
        type="bool",
        default=False,
    )

    def __init__(
        self,
        gateway_facade_builder: GatewayFacade.Builder,
        logger: Logger,
    ) -> None:
        self._gateway_facade_builder = gateway_facade_builder
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
                type="int",
                is_array=True,
            ),
            Command.Argument(
                # Note: This will be removed with the mainnet whitelist
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
                type="int",
            ),
            DeployCommand.wait_for_acceptance_arg,
            DeployCommand.gateway_url_arg,
            DeployCommand.network_arg,
        ]

    async def run(self, args):
        network = args.network or args.gateway_url
        if network is None:
            raise ProtostarException(
                f"Argument `{DeployCommand.gateway_url_arg.name}` or `{DeployCommand.network_arg.name}` is required"
            )

        network_config = NetworkConfig(network)

        self._gateway_facade_builder.set_network(network)
        gateway_facade = self._gateway_facade_builder.build()

        response = await gateway_facade.deploy(
            compiled_contract_path=args.contract,
            inputs=args.inputs,
            token=args.token,
            salt=args.salt,
            wait_for_acceptance=args.wait_for_acceptance,
        )

        explorer_url = network_config.get_contract_explorer_url(response.address)
        explorer_url_msg_lines: List[str] = []
        if explorer_url:
            explorer_url_msg_lines = ["", explorer_url]

        response.log(self._logger, extra_msg=explorer_url_msg_lines)

        return response
