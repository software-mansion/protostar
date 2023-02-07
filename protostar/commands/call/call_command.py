from pathlib import Path
from typing import Any, Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarArgument,
    ProtostarCommand,
    MessengerFactory,
)
from protostar.cli.common_arguments import ABI_PATH_ARG
from protostar.starknet import Address, Selector
from protostar.starknet.contract_abi import ContractAbi
from protostar.starknet_gateway import (
    GatewayFacadeFactory,
    AbiResolver,
    DataTransformerPolicy,
)
from protostar.starknet_gateway.call import CallUseCase, CallInput, CairoOrPythonData

from .call_command_messages import SuccessfulCallMessage


class CallCommand(ProtostarCommand):
    def __init__(
        self,
        project_root_path: Path,
        messenger_factory: MessengerFactory,
        gateway_facade_factory: GatewayFacadeFactory,
    ):
        self._project_root_path = project_root_path
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
            ABI_PATH_ARG,
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
            abi_path=args.abi,
        )
        write(response)
        return response

    async def call(
        self,
        contract_address: Address,
        function_name: str,
        gateway_client: GatewayClient,
        abi_path: Optional[Path] = None,
        inputs: Optional[CairoOrPythonData] = None,
    ) -> SuccessfulCallMessage:
        custom_abi = (
            ContractAbi.from_json_file(self._project_root_path / abi_path)
            if abi_path
            else None
        )
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        abi_resolver = AbiResolver(client=gateway_client)
        data_transformer_policy = DataTransformerPolicy(abi_resolver=abi_resolver)
        call_use_case = CallUseCase(
            gateway_facade=gateway_facade,
            data_transformer_policy=data_transformer_policy,
        )
        response = await call_use_case.execute(
            CallInput(
                address=contract_address,
                selector=Selector(function_name),
                inputs=inputs,
                contract_abi=custom_abi,
            )
        )
        return SuccessfulCallMessage(response)
