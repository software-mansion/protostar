from argparse import Namespace
from dataclasses import dataclass
from typing import Optional

from protostar.cli import (
    ProtostarArgument,
    ProtostarCommand,
    MessengerFactory,
    get_signer,
)
from protostar.cli.common_arguments import (
    ACCOUNT_ADDRESS_ARG,
    PRIVATE_KEY_PATH_ARG,
    SIGNER_CLASS_ARG,
    BLOCK_EXPLORER_ARG,
    WAIT_FOR_ACCEPTANCE_ARG,
    MAX_FEE_ARG,
    INPUTS_ARG,
    TOKEN_ARG,
)
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.io import StructuredMessage, LogColorProvider
from protostar.starknet_gateway import (
    GatewayFacadeFactory,
    SuccessfulDeployResponse,
    BlockExplorer,
    create_block_explorer,
)
from protostar.starknet import Address


@dataclass
class SuccessfulDeployMessage(StructuredMessage):
    response: SuccessfulDeployResponse
    block_explorer: BlockExplorer

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = [
            "Invoke transaction was sent to the Universal Deployer Contract.",
            f"Contract address: {self.response.address}",
        ]
        contract_url = self.block_explorer.create_link_to_contract(
            self.response.address
        )
        if contract_url:
            lines.append(contract_url)
            lines.append("")
        lines.append(f"Transaction hash: 0x{self.response.transaction_hash:064x}")
        tx_url = self.block_explorer.create_link_to_transaction(
            self.response.transaction_hash
        )
        if tx_url:
            lines.append(tx_url)
        return "\n".join(lines)

    def format_dict(self) -> dict:
        return {
            "contract_address": str(self.response.address),
            "transaction_hash": f"0x{self.response.transaction_hash:064x}",
        }


class DeployCommand(ProtostarCommand):
    def __init__(
        self,
        gateway_facade_factory: GatewayFacadeFactory,
        messenger_factory: MessengerFactory,
    ) -> None:
        self._gateway_facade_factory = gateway_facade_factory
        self._messenger_factory = messenger_factory

    @property
    def name(self) -> str:
        return "deploy"

    @property
    def description(self) -> str:
        return "Deploy contracts."

    @property
    def example(self) -> Optional[str]:
        return "protostar deploy 0x4221deadbeef123 --network testnet"

    @property
    def arguments(self):
        return [
            BLOCK_EXPLORER_ARG,
            MAX_FEE_ARG,
            WAIT_FOR_ACCEPTANCE_ARG,
            *MessengerFactory.OUTPUT_ARGUMENTS,
            *NetworkCommandUtil.network_arguments,
            ACCOUNT_ADDRESS_ARG,
            PRIVATE_KEY_PATH_ARG,
            SIGNER_CLASS_ARG,
            ProtostarArgument(
                name="class-hash",
                description="The hash of the declared contract class.",
                type="class_hash",
                is_positional=True,
                is_required=True,
            ),
            INPUTS_ARG,
            TOKEN_ARG,
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
        ]

    async def run(self, args: Namespace):
        network_command_util = NetworkCommandUtil(args)

        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        signer = get_signer(args, network_config, args.account_address)

        write = self._messenger_factory.from_args(args)

        response = await gateway_facade.deploy_via_udc(
            class_hash=args.class_hash,
            signer=signer,
            max_fee=args.max_fee,
            account_address=Address(args.account_address),
            inputs=args.inputs,
            token=args.token,
            salt=args.salt,
            wait_for_acceptance=args.wait_for_acceptance,
        )

        write(
            SuccessfulDeployMessage(
                response=response,
                block_explorer=create_block_explorer(
                    block_explorer_name=args.block_explorer,
                    network=network_config.network_name,
                ),
            )
        )

        return response


def format_successful_deploy_response(
    response: SuccessfulDeployResponse, block_explorer: BlockExplorer
):
    lines: list[str] = []
    lines.append("Deploy transaction was sent.")
    lines.append(f"Contract address: 0x{response.address:064x}")
    contract_url = block_explorer.create_link_to_contract(response.address)
    if contract_url:
        lines.append(contract_url)
        lines.append("")
    lines.append(f"Transaction hash: 0x{response.transaction_hash:064x}")
    tx_url = block_explorer.create_link_to_transaction(response.transaction_hash)
    if tx_url:
        lines.append(tx_url)
    return "\n".join(lines)
