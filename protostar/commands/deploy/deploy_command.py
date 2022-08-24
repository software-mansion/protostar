from logging import Logger
from pathlib import Path
from typing import List, Optional
from protostar.cli.command import Command
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.starknet_gateway import GatewayFacade, format_successful_deploy_response


class DeployCommand(Command):
    wait_for_acceptance_arg = Command.Argument(
        name="wait-for-acceptance",
        description="Waits for transaction to be accepted on chain.",
        type="bool",
        default=False,
    )

    def __init__(
        self,
        logger: Logger,
        project_root_path: Path,
    ) -> None:
        self._logger = logger
        self._project_root_path = project_root_path

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
                type="felt",
                is_array=True,
            ),
            Command.Argument(
                name="token",
                description="Used by whitelisted users for deploying contracts in Alpha MainNet.",
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
                type="felt",
            ),
            DeployCommand.wait_for_acceptance_arg,
            *NetworkCommandUtil.network_arguments,
        ]

    async def run(self, args):
        network_command_util = NetworkCommandUtil(args, self._logger)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        gateway_facade = GatewayFacade(
            gateway_client=gateway_client,
            project_root_path=self._project_root_path,
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
