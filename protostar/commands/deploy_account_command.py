from argparse import Namespace
from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Optional

from starknet_py.net.signer import BaseSigner

from protostar.cli import NetworkCommandUtil, ProtostarCommand, SignableCommandUtil
from protostar.cli.network_command_util import NetworkArgs
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import GatewayFacadeFactory
from protostar.starknet_gateway.gateway_facade import ClassHash, DeployAccountArgs, Fee
from protostar.starknet_gateway.gateway_response import SuccessfulDeployAccountResponse


@dataclass
class DeployAccountCommandArgs(NetworkArgs):
    account_address: str
    salt: int
    account_constructor_input: Optional[list[int]]
    account_class_hash: ClassHash
    nonce: int
    signer: BaseSigner
    max_fee: Fee

    @classmethod
    def from_args(cls, args: Namespace):
        logger = getLogger()
        network_util = NetworkCommandUtil(args, logger=logger)
        network_config = network_util.get_network_config()
        gateway_client = network_util.get_gateway_client()
        signer = SignableCommandUtil(args, logger=logger).get_signer(
            network_config=network_config
        )

        assert signer is not None
        return cls(
            account_address=args.account_address,
            nonce=args.nonce,
            account_class_hash=args.account_class_hash,
            account_constructor_input=args.account_constructor_input or [],
            salt=args.salt,
            signer=signer,
            max_fee=args.max_fee,
            gateway_client=gateway_client,
            chain_id=args.chain_id,
        )


class DeployAccountCommand(ProtostarCommand):
    def __init__(
        self,
        logger: Logger,
        gateway_facade_factory: GatewayFacadeFactory,
    ) -> None:
        self._logger = logger
        self._gateway_facade_factory = gateway_facade_factory

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
        ]

    async def run(self, args: Namespace):
        typed_args = DeployAccountCommandArgs.from_args(args)
        self._validate_cli_args(typed_args)
        deploy_account_args = self._map_typed_args_to_deploy_account_args(typed_args)
        response = await self._send_deploy_account_tx(
            deploy_account_args=deploy_account_args, typed_args=typed_args
        )
        self._log_response(response)

    def _validate_cli_args(self, typed_args: DeployAccountCommandArgs):
        if typed_args.max_fee == "auto":
            raise ProtostarException(
                "Protostar can't auto-estimate max fee for the DeployAccount transaction."
            )

    def _map_typed_args_to_deploy_account_args(
        self,
        typed_args: DeployAccountCommandArgs,
    ) -> DeployAccountArgs:
        return DeployAccountArgs(
            account_address=int(typed_args.account_address, base=0),
            account_class_hash=typed_args.account_class_hash,
            account_address_salt=typed_args.salt,
            nonce=typed_args.nonce,
            signer=typed_args.signer,
            account_constructor_input=typed_args.account_constructor_input,
            max_fee=1,
        )

    async def _send_deploy_account_tx(
        self,
        typed_args: DeployAccountCommandArgs,
        deploy_account_args: DeployAccountArgs,
    ):

        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=typed_args.gateway_client, logger=None
        )
        return await gateway_facade.deploy_account(args=deploy_account_args)

    def _log_response(self, response: SuccessfulDeployAccountResponse):
        return self._logger.info(
            "\n".join(
                [
                    "DeployAccount transaction was sent.",
                    f"Transaction hash: 0x{response.transaction_hash:064x}",
                ]
            )
        )


class AutoEstimateMaxFeeException(ProtostarException):
    def __init__(self):
        super().__init__(
            "Protostar can't auto-estimate max fee for the DeployAccount transaction.\n"
            "Please provide explicit value."
        )
