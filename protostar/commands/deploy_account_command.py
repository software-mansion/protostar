from argparse import Namespace
from dataclasses import dataclass
from typing import Optional

from starknet_py.net.signer import BaseSigner

from protostar.cli import (
    NetworkCommandUtil,
    ProtostarArgument,
    ProtostarCommand,
    SignableCommandUtil,
    MessengerFactory,
)
from protostar.cli.common_arguments import (
    ACCOUNT_CLASS_HASH_ARG,
    ACCOUNT_ADDRESS_SALT_ARG,
    ACCOUNT_CONSTRUCTOR_INPUT,
    MAX_FEE_ARG,
)
from protostar.cli.network_command_util import NetworkArgs
from protostar.io import StructuredMessage, LogColorProvider
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import GatewayFacadeFactory
from protostar.starknet_gateway.gateway_facade import DeployAccountArgs
from protostar.starknet_gateway.type import ClassHash, Fee
from protostar.starknet_gateway.gateway_response import SuccessfulDeployAccountResponse
from protostar.starknet import Address


@dataclass
class DeployAccountCommandArgs(NetworkArgs):
    account_address_salt: int
    account_constructor_input: Optional[list[int]]
    account_class_hash: ClassHash
    nonce: int
    signer: BaseSigner
    max_fee: Fee

    @classmethod
    def from_args(cls, args: Namespace):
        network_util = NetworkCommandUtil(args)
        network_config = network_util.get_network_config()
        gateway_client = network_util.get_gateway_client()
        signer = SignableCommandUtil(args).get_signer(network_config=network_config)

        assert signer is not None
        return cls(
            nonce=args.nonce,
            account_class_hash=args.account_class_hash,
            account_constructor_input=args.account_constructor_input or [],
            account_address_salt=args.account_address_salt,
            signer=signer,
            max_fee=args.max_fee,
            gateway_client=gateway_client,
            chain_id=args.chain_id,
        )


@dataclass
class SuccessfulDeployAccountMessage(StructuredMessage):
    response: SuccessfulDeployAccountResponse

    def format_human(self, fmt: LogColorProvider) -> str:
        return f"""\
DeployAccount transaction was sent.
Transaction hash: 0x{self.response.transaction_hash:064x}
"""

    def format_dict(self) -> dict:
        return {
            "transaction_hash": f"0x{self.response.transaction_hash:064x}",
        }


class DeployAccountCommand(ProtostarCommand):
    def __init__(
        self,
        gateway_facade_factory: GatewayFacadeFactory,
        messenger_factory: MessengerFactory,
    ) -> None:
        self._gateway_facade_factory = gateway_facade_factory
        self._messenger_factory = messenger_factory

    @property
    def name(self) -> str:
        return "deploy-account"

    @property
    def description(self) -> str:
        return "Sends deploy-account transaction. The account contract must be already declared and prefunded."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *NetworkCommandUtil.network_arguments,
            *SignableCommandUtil.signable_arguments,
            *MessengerFactory.OUTPUT_ARGUMENTS,
            ACCOUNT_CLASS_HASH_ARG,
            ACCOUNT_ADDRESS_SALT_ARG,
            ACCOUNT_CONSTRUCTOR_INPUT,
            ProtostarArgument(
                name="nonce",
                description="Protects against the replay attacks.",
                type="int",
                default=0,
            ),
            ProtostarArgument(
                name=MAX_FEE_ARG.name,
                description="Max amount of Wei you are willing to pay for the transaction",
                type="wei",
                is_required=True,
            ),
        ]

    async def run(self, args: Namespace):
        write = self._messenger_factory.from_args(args)

        typed_args = DeployAccountCommandArgs.from_args(args)
        deploy_account_args = self._map_typed_args_to_deploy_account_args(typed_args)

        response = await self._send_deploy_account_tx(
            deploy_account_args=deploy_account_args, typed_args=typed_args
        )

        write(SuccessfulDeployAccountMessage(response))

        return response

    def _map_typed_args_to_deploy_account_args(
        self,
        typed_args: DeployAccountCommandArgs,
    ) -> DeployAccountArgs:
        if typed_args.max_fee == "auto":
            raise AutoEstimateMaxFeeException()

        constructor_calldata = (
            typed_args.account_constructor_input
            if typed_args.account_constructor_input is not None
            else []
        )

        return DeployAccountArgs(
            account_address=Address.from_class_hash(
                class_hash=typed_args.account_class_hash,
                salt=typed_args.account_address_salt,
                constructor_calldata=constructor_calldata,
            ),
            account_class_hash=typed_args.account_class_hash,
            account_address_salt=typed_args.account_address_salt,
            nonce=typed_args.nonce,
            signer=typed_args.signer,
            account_constructor_input=typed_args.account_constructor_input,
            max_fee=typed_args.max_fee,
        )

    async def _send_deploy_account_tx(
        self,
        typed_args: DeployAccountCommandArgs,
        deploy_account_args: DeployAccountArgs,
    ) -> SuccessfulDeployAccountResponse:
        gateway_facade = self._gateway_facade_factory.create(typed_args.gateway_client)
        return await gateway_facade.deploy_account(args=deploy_account_args)


class AutoEstimateMaxFeeException(ProtostarException):
    def __init__(self):
        super().__init__(
            "Protostar cannot estimate max fee for the DeployAccount transaction.\n"
            "Please provide an explicit value."
        )
