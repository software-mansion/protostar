from typing import Any, Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarArgument,
    ProtostarCommand,
    MessengerFactory,
)
from protostar.starknet_gateway import (
    GatewayFacadeFactory,
    AbiResolver,
    DataTransformer,
)
from protostar.starknet import Address, Selector
from protostar.starknet_gateway.call import CallUseCase, CallInput, Calldata

from .call_command_messages import SuccessfulCallMessage


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
                # pylint: disable=line-too-long
                description="Inputs to the function being called, represented either by a list of space-delimited values (`1 2 3`) or by a mapping of their names to their values (`a=11 b=12 c=13`).",
                type="input",
                value_parser="list_or_dict",
            ),
        ]

    async def run(self, args: Any) -> SuccessfulCallMessage:
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
        inputs: Optional[Calldata] = None,
    ) -> SuccessfulCallMessage:
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        abi_resolver = AbiResolver(client=gateway_client)
        data_transformer = DataTransformer(abi_resolver=abi_resolver)
        call_use_case = CallUseCase(
            gateway_facade=gateway_facade,
            data_transformer=data_transformer,
        )
        response = await call_use_case.execute(
            CallInput(
                address=contract_address,
                selector=Selector(function_name),
                inputs=inputs,
                abi=None,
            )
        )
        return SuccessfulCallMessage(response)
