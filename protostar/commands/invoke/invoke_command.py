from typing import Any, Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer import BaseSigner

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarCommand,
    get_signer,
    MessengerFactory,
)
from protostar.cli.common_arguments import (
    ACCOUNT_ADDRESS_ARG,
    PRIVATE_KEY_PATH_ARG,
    SIGNER_CLASS_ARG,
    BLOCK_EXPLORER_ARG,
    MAX_FEE_ARG,
    WAIT_FOR_ACCEPTANCE_ARG,
    CONTRACT_ADDRESS_ARG,
    FUNCTION_ARG,
    INPUTS_ARG,
)
from protostar.io.output import Messenger
from protostar.starknet import Address, CairoOrPythonData, Selector
from protostar.starknet_gateway import (
    Fee,
    GatewayFacadeFactory,
    create_block_explorer,
    AccountManager,
    DataTransformerPolicy,
    AbiResolver,
    AccountConfig,
)
from protostar.starknet_gateway.block_explorer.block_explorer import BlockExplorer
from protostar.starknet_gateway.invoke import InvokeUseCase, InvokeInput, InvokeOutput

from .messages import (
    SendingInvokeTransactionMessage,
    InvokeTransactionSentMessage,
    TransactionAcceptedOnL2Message,
    WaitingForAcceptanceMessage,
)


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
            ACCOUNT_ADDRESS_ARG,
            PRIVATE_KEY_PATH_ARG,
            SIGNER_CLASS_ARG,
            *NetworkCommandUtil.network_arguments,
            *MessengerFactory.OUTPUT_ARGUMENTS,
            BLOCK_EXPLORER_ARG,
            CONTRACT_ADDRESS_ARG,
            FUNCTION_ARG,
            INPUTS_ARG,
            MAX_FEE_ARG,
            WAIT_FOR_ACCEPTANCE_ARG,
        ]

    async def run(self, args: Any):
        write = self._messenger_factory.from_args(args)
        network_command_util = NetworkCommandUtil(args)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        signer = get_signer(args, network_config, args.account_address)
        block_explorer = create_block_explorer(
            block_explorer_name=args.block_explorer,
            network=network_config.network_name,
        )
        return await self.invoke(
            contract_address=args.contract_address,
            function_name=args.function,
            inputs=args.inputs,
            gateway_client=gateway_client,
            gateway_url=network_config.gateway_url,
            signer=signer,
            max_fee=args.max_fee,
            write=write,
            block_explorer=block_explorer,
            wait_for_acceptance=args.wait_for_acceptance,
            account_address=args.account_address,
        )

    async def invoke(
        self,
        contract_address: Address,
        function_name: str,
        gateway_client: GatewayClient,
        gateway_url: str,
        max_fee: Fee,
        signer: BaseSigner,
        account_address: Address,
        write: Messenger,
        block_explorer: BlockExplorer,
        inputs: Optional[CairoOrPythonData] = None,
        wait_for_acceptance: bool = False,
    ) -> InvokeOutput:
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        account_manager = AccountManager(
            account_config=AccountConfig(
                address=account_address,
                signer=signer,
            ),
            client=gateway_facade,
            gateway_url=gateway_url,
        )
        abi_resolver = AbiResolver(client=gateway_client)
        data_transformer_policy = DataTransformerPolicy(abi_resolver=abi_resolver)
        use_case_input = InvokeInput(
            address=contract_address,
            selector=Selector(function_name),
            calldata=inputs,
            max_fee=max_fee,
            contract_abi=None,
        )
        use_case = InvokeUseCase(
            account_manager=account_manager,
            client=gateway_facade,
            data_transformer_policy=data_transformer_policy,
        )

        write(SendingInvokeTransactionMessage())
        invoke_output = await use_case.execute(use_case_input)
        write(
            InvokeTransactionSentMessage(
                tx_url=block_explorer.create_link_to_transaction(
                    invoke_output.transaction_hash
                ),
                response=invoke_output,
            )
        )
        if wait_for_acceptance:
            write(WaitingForAcceptanceMessage())
            await use_case.wait_for_acceptance(tx_hash=invoke_output.transaction_hash)
            write(TransactionAcceptedOnL2Message())
        return invoke_output
