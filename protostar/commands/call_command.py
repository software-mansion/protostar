import json
from dataclasses import dataclass
from typing import Any, Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarArgument,
    ProtostarCommand,
    MessengerFactory,
)
from protostar.io import LogColorProvider, StructuredMessage
from protostar.starknet_gateway import GatewayFacadeFactory
from protostar.starknet import Address


@dataclass
class SuccessfulCallMessage(StructuredMessage):
    response: Any

    def format_human(self, fmt: LogColorProvider) -> str:
        return f"""\
{fmt.colorize("GREEN", "Call successful.")}
Response:
{json.dumps(self.response._asdict(), indent=4)}\
"""

    def format_dict(self) -> dict:
        return self.response._asdict()


class CallCommand(ProtostarCommand):
    def __init__(
        self,
        messenger_factory: MessengerFactory,
        gateway_facade_factory: GatewayFacadeFactory,
    ):
        self._messenger_factory = messenger_factory
        self._gateway_facade_factory = gateway_facade_factory

    @property
    def name(self) -> str:
        return "call"

    @property
    def description(self) -> str:
        return "Calls a contract on StarkNet with given parameters"

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *NetworkCommandUtil.network_arguments,
            *MessengerFactory.OUTPUT_ARGUMENTS,
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
        ]

    async def run(self, args: Any):
        write = self._messenger_factory.from_args(args)

        network_command_util = NetworkCommandUtil(args)
        gateway_client = network_command_util.get_gateway_client()

        response = await self.call(
            contract_address=args.contract_address,
            function_name=args.function,
            inputs=args.inputs,
            gateway_client=gateway_client,
        )

        write(response)

        return response

    async def call(
        self,
        contract_address: Address,
        function_name: str,
        gateway_client: GatewayClient,
        inputs: Optional[list[int]] = None,
    ) -> SuccessfulCallMessage:
        gateway_facade = self._gateway_facade_factory.create(gateway_client)

        response = await gateway_facade.call(
            address=contract_address,
            function_name=function_name,
            inputs=inputs,
        )

        return SuccessfulCallMessage(response)
