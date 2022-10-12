from logging import Logger
from typing import List, Optional

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cli.command import Command
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.starknet_gateway import (
    GatewayFacadeFactory,
    format_successful_deploy_response,
)


class DeployCommand(ProtostarCommand):
    wait_for_acceptance_arg = ProtostarArgument(
        name="wait-for-acceptance",
        description="Waits for transaction to be accepted on chain.",
        type="bool",
        default=False,
    )

    def __init__(
        self,
        logger: Logger,
        gateway_facade_factory: GatewayFacadeFactory,
    ) -> None:
        self._logger = logger
        self._gateway_facade_factory = gateway_facade_factory

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "Deploy contracts."

    @property
    def example(self) -> Optional[str]:
        return "protostar deploy ./build/main.json --network alpha-goerli"

    @property
    def arguments(self):
        return [
            ProtostarArgument(
                name="contract",
                description="The path to the compiled contract.",
                type="path",
                is_required=True,
                is_positional=True,
            ),
            ProtostarArgument(
                name="inputs",
                short_name="i",
                description=(
                    "The inputs to the constructor. "
                    "Calldata arguments may be of any type that does not contain pointers.\n"
                    # pylint: disable=line-too-long
                    "[Read more about representing Cairo data types in the CLI.](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata)"
                ),
                type="felt",
                is_array=True,
            ),
            ProtostarArgument(
                name="token",
                description="Used by whitelisted users for deploying contracts in Alpha MainNet.",
                type="str",
            ),
            ProtostarArgument(
                name="salt",
                description=(
                    "An optional salt controlling where the contract will be deployed. "
                    "The contract deployment address is determined by the hash "
                    "of contract, salt and caller. "
                    "If the salt is not supplied, the contract will be deployed with a random salt."
                ),
                type="felt",
            ),
            DeployCommand.wait_for_acceptance_arg,
            *NetworkCommandUtil.network_arguments,
        ]

    async def run(self, args):
        self._logger.warning(
            "`protostar deploy` will be removed in the future release\n"
            "https://docs.starknet.io/docs/Blocks/transactions/#deploy-transaction"
        )

        network_command_util = NetworkCommandUtil(args, self._logger)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=gateway_client, logger=None
        )

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

        self._logger.info(
            format_successful_deploy_response(
                response, extra_msg=explorer_url_msg_lines
            )
        )

        return response
