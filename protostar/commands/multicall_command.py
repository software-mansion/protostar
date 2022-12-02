from argparse import Namespace
from pathlib import Path
from typing import Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import (
    ProtostarCommand,
    ProtostarArgument,
    NetworkCommandUtil,
    SignableCommandUtil,
)
from protostar.starknet_gateway import AccountManager, GatewayFacadeFactory
from protostar.starknet_gateway.account_manager import Account
from protostar.starknet_gateway.multicall import (
    MulticallUseCase,
    MulticallInput,
    interpret_multicall_file_content,
)


class MulticallCommand(ProtostarCommand):
    def __init__(self, gateway_facade_factory: GatewayFacadeFactory) -> None:
        super().__init__()
        self._gateway_facade_factory = gateway_facade_factory

    @property
    def name(self) -> str:
        return "multicall"

    @property
    def description(self) -> str:
        return "Execute multiple deploy (via UDC) and invoke calls ensuring atomicity."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *NetworkCommandUtil.network_arguments,
            *SignableCommandUtil.signable_arguments,
            ProtostarArgument(
                name="file",
                description="Path to the file declaring calls.",
                type="path",
                is_required=True,
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        network_util = NetworkCommandUtil(args)
        network_config = network_util.get_network_config()
        gateway_client = network_util.get_gateway_client()
        signer = SignableCommandUtil(args).get_signer(network_config=network_config)
        return await self.multicall(
            file=args.file,
            gateway_client=gateway_client,
            gateway_url=network_config.gateway_url,
            account=Account(address=args.account_address, signer=signer),
        )

    async def multicall(
        self,
        file: Path,
        gateway_client: GatewayClient,
        account: Account,
        gateway_url: str,
    ):
        account_manager = AccountManager(account, gateway_url=gateway_url)
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        multicall_use_case = MulticallUseCase(
            account_manager=account_manager, client=gateway_facade
        )
        file_content = file.read_text()
        calls = interpret_multicall_file_content(file_content)
        multicall_input = MulticallInput(calls=calls, max_fee="auto")
        return await multicall_use_case.execute(multicall_input)
