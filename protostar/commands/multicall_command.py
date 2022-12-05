from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Optional

from starknet_py.net.gateway_client import GatewayClient

from protostar.cli import (
    ProtostarCommand,
    ProtostarArgument,
    NetworkCommandUtil,
    SignableCommandUtil,
    MessengerFactory,
)
from protostar.cli.common_arguments import BLOCK_EXPLORER_ARG
from protostar.io import Messenger, StructuredMessage, format_as_table
from protostar.io.log_color_provider import LogColorProvider
from protostar.starknet_gateway import (
    AccountManager,
    GatewayFacadeFactory,
    BlockExplorer,
    Account,
    create_block_explorer,
)
from protostar.starknet_gateway.multicall import (
    MulticallUseCase,
    MulticallInput,
    MulticallOutput,
    interpret_multicall_file_content,
    MULTICALL_FILE_EXAMPLE,
)


@dataclass
class MulticallOutputMessage(StructuredMessage):
    multicall_output: MulticallOutput
    url: Optional[str]

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = []
        lines.append("Multicall has been sent.")
        table_lines = format_as_table(
            {
                "transaction hash": f"0x{self.multicall_output.transaction_hash:064x}",
                **self._get_json_friendly_contract_address_map(),
            }
        )
        lines += table_lines
        if self.url:
            lines.append(self.url)
        return dedent("\n".join(lines))

    def format_dict(self) -> dict:
        return {
            "transaction_hash": f"0x{self.multicall_output.transaction_hash:064x}",
            **self._get_json_friendly_contract_address_map(),
        }

    def _get_json_friendly_contract_address_map(self):
        result = {}
        for key, value in self.multicall_output.deployed_contract_addresses.items():
            key_str = key.value
            result[key_str] = str(value)
        return result


class MulticallCommand(ProtostarCommand):
    def __init__(
        self,
        gateway_facade_factory: GatewayFacadeFactory,
        messenger_factory: MessengerFactory,
    ) -> None:
        super().__init__()
        self._gateway_facade_factory = gateway_facade_factory
        self._messenger_factory = messenger_factory

    @property
    def name(self) -> str:
        return "multicall"

    @property
    def description(self) -> str:
        return "Execute multiple deploy (via UDC) or invoke calls in a single transaction ensuring atomicity."

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *NetworkCommandUtil.network_arguments,
            *SignableCommandUtil.signable_arguments,
            *MessengerFactory.OUTPUT_ARGUMENTS,
            BLOCK_EXPLORER_ARG,
            ProtostarArgument(
                name="file",
                description=(
                    "Path to a TOML file with call declarations. File example:\n\n"
                    f"```toml\n{MULTICALL_FILE_EXAMPLE}\n```"
                ),
                type="path",
                is_required=True,
                is_positional=True,
            ),
        ]

    async def run(self, args: Namespace):
        write = self._messenger_factory.from_args(args)
        network_util = NetworkCommandUtil(args)
        network_config = network_util.get_network_config()
        gateway_client = network_util.get_gateway_client()
        signer = SignableCommandUtil(args).get_signer(network_config=network_config)
        block_explorer = create_block_explorer(
            block_explorer_name=args.block_explorer,
            network=network_config.network_name,
        )
        return await self.multicall(
            file=args.file,
            gateway_client=gateway_client,
            gateway_url=network_config.gateway_url,
            account=Account(address=args.account_address, signer=signer),
            write=write,
            explorer=block_explorer,
        )

    async def multicall(
        self,
        file: Path,
        gateway_client: GatewayClient,
        account: Account,
        gateway_url: str,
        write: Messenger,
        explorer: BlockExplorer,
    ):
        account_manager = AccountManager(account, gateway_url=gateway_url)
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        multicall_use_case = MulticallUseCase(
            account_manager=account_manager, client=gateway_facade
        )
        file_content = file.read_text()
        calls = interpret_multicall_file_content(file_content)
        multicall_input = MulticallInput(calls=calls, max_fee="auto")
        result = await multicall_use_case.execute(multicall_input)
        tx_url = explorer.create_link_to_transaction(result.transaction_hash)
        write(MulticallOutputMessage(multicall_output=result, url=tx_url))
        return result
