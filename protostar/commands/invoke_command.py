import json
from dataclasses import dataclass
from typing import Any, Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer import BaseSigner
from starkware.starknet.public.abi import AbiType

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarArgument,
    ProtostarCommand,
    SignableCommandUtil,
    MessengerFactory,
)
from protostar.cli.common_arguments import (
    BLOCK_EXPLORER_ARG,
    MAX_FEE_ARG,
    WAIT_FOR_ACCEPTANCE_ARG, ABI_ARG,
)
from protostar.io import StructuredMessage, LogColorProvider
from protostar.starknet import Address
from protostar.starknet_gateway import (
    Fee,
    GatewayFacadeFactory,
    SuccessfulInvokeResponse,
    create_block_explorer,
)


@dataclass
class SuccessfulInvokeMessage(StructuredMessage):
    response: SuccessfulInvokeResponse
    tx_url: Optional[str]

    def format_human(self, fmt: LogColorProvider) -> str:
        message = f"""\
Invoke transaction was sent.
Transaction hash: 0x{self.response.transaction_hash:064x}
"""
        if self.tx_url:
            message += f"{self.tx_url}\n"

        return message

    def format_dict(self) -> dict:
        return {
            "transaction_hash": f"0x{self.response.transaction_hash:064x}",
        }


class InvokeCommand(ProtostarCommand):
    def __init__(
        self,
        gateway_facade_factory: GatewayFacadeFactory,
        messenger_factory: MessengerFactory,
    ):
        self._gateway_facade_factory = gateway_facade_factory
        self._messenger_factory = messenger_factory

    @property
    def name(self) -> str:
        return "invoke"

    @property
    def description(self) -> str:
        return "Sends an invoke transaction to the StarkNet sequencer."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *SignableCommandUtil.signable_arguments,
            *NetworkCommandUtil.network_arguments,
            *MessengerFactory.OUTPUT_ARGUMENTS,
            BLOCK_EXPLORER_ARG,
            ABI_ARG,
            ProtostarArgument(
                name="contract-address",
                description="The address of the contract being called.",
                type="address",
                is_required=True,
            ),
            ProtostarArgument(
                name="function",
                description="The name of the function being called.",
                type="str",
                is_required=True,
            ),
            ProtostarArgument(
                name="inputs",
                description="Inputs to the function being called, represented by a list of space-delimited values.",
                type="felt",
                is_array=True,
            ),
            MAX_FEE_ARG,
            WAIT_FOR_ACCEPTANCE_ARG,
        ]

    async def run(self, args: Any):
        write = self._messenger_factory.from_args(args)

        network_command_util = NetworkCommandUtil(args)
        signable_command_util = SignableCommandUtil(args)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        signer = signable_command_util.get_signer(network_config)

        block_explorer = create_block_explorer(
            block_explorer_name=args.block_explorer,
            network=network_config.network_name,
        )

        abi = None
        if args.abi:
            abi = json.loads(args.abi.read_text("utf-8"))

        response = await self.invoke(
            contract_address=args.contract_address,
            function_name=args.function,
            inputs=args.inputs,
            gateway_client=gateway_client,
            abi=abi,
            signer=signer,
            max_fee=args.max_fee,
            wait_for_acceptance=args.wait_for_acceptance,
            account_address=args.account_address,
        )

        write(
            SuccessfulInvokeMessage(
                response=response,
                tx_url=block_explorer.create_link_to_transaction(
                    response.transaction_hash
                ),
            )
        )

        return response

    async def invoke(
        self,
        contract_address: Address,
        function_name: str,
        gateway_client: GatewayClient,
        max_fee: Fee,
        signer: BaseSigner,
        account_address: Address,
        abi: Optional[AbiType] = None,
        inputs: Optional[list[int]] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulInvokeResponse:
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        return await gateway_facade.invoke(
            contract_address=contract_address,
            function_name=function_name,
            inputs=inputs,
            max_fee=max_fee,
            signer=signer,
            abi=abi,
            account_address=account_address,
            wait_for_acceptance=wait_for_acceptance,
        )
