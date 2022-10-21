import json
from logging import Logger
from typing import Any, Optional, Dict

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarArgument,
    ProtostarCommand,
)
from protostar.starknet_gateway import GatewayFacadeFactory


class CallCommand(ProtostarCommand):
    def __init__(
        self,
        logger: Logger,
        gateway_facade_factory: GatewayFacadeFactory,
    ):
        self._logger = logger
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
            ProtostarArgument(
                name="contract-address",
                description="The address of the contract being called.",
                type="str",
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
        network_command_util = NetworkCommandUtil(args, self._logger)
        gateway_client = network_command_util.get_gateway_client()

        return await self.call(
            contract_address=args.contract_address,
            function_name=args.function,
            inputs=args.inputs,
            gateway_client=gateway_client,
        )

    async def call(
        self,
        contract_address: int,
        function_name: str,
        gateway_client: GatewayClient,
        inputs: Optional[list[int]] = None,
    ):
        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=gateway_client, logger=None
        )
        response = await gateway_facade.call(
            address=contract_address,
            function_name=function_name,
            inputs=inputs,
        )
        self._logger.info(self._format_successful_call_response(response._asdict()))

        return response

    @staticmethod
    def _format_successful_call_response(response: Dict[str, Any]):
        return "\n".join(
            [
                "Call successful.",
                "Response:",
                json.dumps(response, indent=4),
            ]
        )
