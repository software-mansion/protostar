from logging import Logger
from pathlib import Path
from typing import List, Optional

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer import BaseSigner

from protostar.cli import ProtostarArgument, ProtostarCommand
from protostar.cli.command import Command
from protostar.cli.network_command_util import NetworkCommandUtil
from protostar.cli.signable_command_util import SignableCommandUtil
from protostar.commands.deploy_command import DeployCommand
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import (
    Fee,
    GatewayFacadeFactory,
    NetworkConfig,
    SuccessfulDeclareResponse,
    format_successful_declare_response,
)


class DeclareCommand(ProtostarCommand):
    def __init__(
        self,
        logger: Logger,
        gateway_facade_factory: GatewayFacadeFactory,
    ):
        self._logger = logger
        self._gateway_facade_factory = gateway_facade_factory

    @property
    def name(self) -> str:
        return "declare"

    @property
    def description(self) -> str:
        return "Sends a declare transaction to StarkNet."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *SignableCommandUtil.signable_arguments,
            *NetworkCommandUtil.network_arguments,
            Command.Argument(
                name="contract",
                description="Path to compiled contract.",
                type="path",
                is_positional=True,
                is_required=True,
            ),
            Command.Argument(
                name="token",
                description="Used for declaring contracts in Alpha MainNet.",
                type="str",
            ),
            ProtostarArgument(
                name="max-fee",
                description=(
                    "The maximum fee that the sender is willing to pay for the transaction. "
                    'Provide "auto" to auto estimate the fee.'
                ),
                type="fee",
            ),
            DeployCommand.wait_for_acceptance_arg,
        ]

    async def run(self, args) -> SuccessfulDeclareResponse:
        assert isinstance(args.contract, Path)
        assert args.gateway_url is None or isinstance(args.gateway_url, str)
        assert args.network is None or isinstance(args.network, str)
        assert args.token is None or isinstance(args.token, str)
        assert isinstance(args.wait_for_acceptance, bool)

        network_command_util = NetworkCommandUtil(args, self._logger)
        signable_command_util = SignableCommandUtil(args, self._logger)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        signer = signable_command_util.get_signer(network_config)

        return await self.declare(
            compiled_contract_path=args.contract,
            signer=signer,
            account_address=args.account_address,
            gateway_client=gateway_client,
            network_config=network_config,
            token=args.token,
            wait_for_acceptance=args.wait_for_acceptance,
            max_fee=args.max_fee,
        )

    async def declare(
        self,
        compiled_contract_path: Path,
        network_config: NetworkConfig,
        gateway_client: GatewayClient,
        account_address: Optional[str] = None,
        signer: Optional[BaseSigner] = None,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False,
        max_fee: Optional[Fee] = None,
    ) -> SuccessfulDeclareResponse:

        gateway_facade = self._gateway_facade_factory.create(
            gateway_client=gateway_client, logger=None
        )
        if signer and account_address is not None:
            if max_fee is None:
                raise ProtostarException(
                    "Argument `max-fee` is required for transactions V1."
                )
            response = await gateway_facade.declare(
                compiled_contract_path=compiled_contract_path,
                signer=signer,
                account_address=account_address,
                wait_for_acceptance=wait_for_acceptance,
                token=token,
                max_fee=max_fee,
            )
        else:
            response = await gateway_facade.declare_v0(
                compiled_contract_path=compiled_contract_path,
                wait_for_acceptance=wait_for_acceptance,
                token=token,
            )

        explorer_url = network_config.get_contract_explorer_url(response.class_hash)
        explorer_url_msg_lines: List[str] = []
        if explorer_url:
            explorer_url_msg_lines = ["", explorer_url]

        self._logger.info(
            format_successful_declare_response(
                response, extra_msg=explorer_url_msg_lines
            )
        )

        return response
