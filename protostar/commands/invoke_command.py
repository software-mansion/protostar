from logging import Logger
from typing import Any, Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer import BaseSigner

from protostar.cli import Command
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.cli.signable_command_util import SignableCommandUtil
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import GatewayFacadeFactory, SuccessfulInvokeResponse
from protostar.starknet_gateway.gateway_facade import Fee


class InvokeCommand(Command):
    def __init__(
        self,
        logger: Logger,
        gateway_facade_factory: GatewayFacadeFactory,
    ):
        self._logger = logger
        self._gateway_facade_factory = gateway_facade_factory

    @property
    def name(self) -> str:
        return "invoke"

    @property
    def description(self) -> str:
        return "Sends a transaction to the StarkNet sequencer."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self) -> list[Command.Argument]:
        return [
            *SignableCommandUtil.signable_arguments,
            *NetworkCommandUtil.network_arguments,
            Command.Argument(
                name="address",
                description="The address of the contract being called.",
                type="int",
                is_required=True,
            ),
            Command.Argument(
                name="function",
                description="The name of the function being called.",
                type="str",
                is_required=True,
            ),
            Command.Argument(
                name="inputs",
                description="The name of the function being called.",
                type="felt",
                is_required=True,
                is_array=True,
            ),
            Command.Argument(
                name="max-fee",
                description=(
                    "The maximum fee that the sender is willing to pay for the transaction. "
                    'Provide "auto" to auto estimate the fee.'
                ),
                type="fee",
            ),
            Command.Argument(
                name="wait-for-acceptance",
                description="Waits for transaction to be accepted on chain.",
                type="bool",
                default=False,
            ),
        ]

    async def run(self, args: Any) -> Any:
        network_command_util = NetworkCommandUtil(args, self._logger)
        signable_command_util = SignableCommandUtil(args, self._logger)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        signer = signable_command_util.get_signer(network_config)

        return self.invoke(
            address=args.address,
            function=args.function,
            inputs=args.inputs,
            gateway_client=gateway_client,
            signer=signer,
            max_fee=args.max_fee,
            wait_for_acceptance=args.wait_for_acceptance,
            account_address=args.account_address,
        )

    async def invoke(
        self,
        address: int,
        function: str,
        inputs: list[int],
        gateway_client: GatewayClient,
        signer: Optional[BaseSigner] = None,
        account_address: Optional[str] = None,
        max_fee: Optional[Fee] = None,
        wait_for_acceptance: bool = False,
    ):
        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=gateway_client, logger=None
        )
        if signer is None:
            raise ProtostarException(
                "Argument `signer` is required for transactions V1."
            )
        if account_address is None:
            raise ProtostarException(
                "Argument `account_address` is required for transactions V1."
            )
        if max_fee is None:
            raise ProtostarException(
                "Argument `max-fee` is required for transactions V1."
            )
        response = await gateway_facade.invoke(
            contract_address=address,
            function_name=function,
            inputs=inputs,
            max_fee=max_fee if isinstance(max_fee, int) else None,
            auto_estimate_fee=max_fee == "auto",
            signer=signer,
            account_address=account_address,
            wait_for_acceptance=wait_for_acceptance,
        )
        self._logger.info(self.format_successful_invoke_response(response))

        return response

    @staticmethod
    def format_successful_invoke_response(response: SuccessfulInvokeResponse):
        return "\n".join(
            [
                "Invoke transaction was sent.",
                f"Contract address: 0x{response.address:064x}",
                "Transaction hash: {gateway_response['transaction_hash']}",
            ]
        )
