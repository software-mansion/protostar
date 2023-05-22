from argparse import Namespace
from typing import Optional, Any

from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.signer import BaseSigner

from protostar.cli import (
    ProtostarCommand,
    NetworkCommandUtil,
    MessengerFactory,
    ProtostarArgument,
    get_signer,
)
from protostar.cli.common_arguments import (
    ACCOUNT_ADDRESS_ARG,
    PRIVATE_KEY_PATH_ARG,
    SIGNER_CLASS_ARG,
    BLOCK_EXPLORER_ARG,
    TOKEN_ARG,
    MAX_FEE_ARG,
    WAIT_FOR_ACCEPTANCE_ARG,
)
from protostar.commands.cairo1_commands.fetch_from_scarb import (
    fetch_linked_libraries_from_scarb,
)

from protostar.commands.declare.declare_messages import SuccessfulDeclareMessage
from protostar.compiler.cairo1_contract_compiler import Cairo1ContractCompiler
from protostar.contract_path_resolver import ContractPathResolver
from protostar.starknet import Address
from protostar.starknet_gateway import (
    SuccessfulDeclareResponse,
    create_block_explorer,
    Fee,
    GatewayFacadeFactory,
)


class DeclareCairo1Command(ProtostarCommand):
    def __init__(
        self,
        contract_path_resolver: ContractPathResolver,
        gateway_facade_factory: GatewayFacadeFactory,
        messenger_factory: MessengerFactory,
    ):
        self._gateway_facade_factory = gateway_facade_factory
        self._messenger_factory = messenger_factory
        self._contract_path_resolver = contract_path_resolver

    @property
    def name(self) -> str:
        return "declare-cairo1"

    @property
    def description(self) -> str:
        return "Sends a declare transaction to Starknet."

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
            ProtostarArgument(
                name="contract",
                description="Name of the contract defined in the protostar.toml",
                type="str",
                is_positional=True,
                is_required=True,
            ),
            TOKEN_ARG,
            MAX_FEE_ARG,
            WAIT_FOR_ACCEPTANCE_ARG,
        ]

    async def run(self, args: Namespace) -> Any:
        write = self._messenger_factory.from_args(args)

        assert isinstance(args.contract, str)
        assert args.gateway_url is None or isinstance(args.gateway_url, str)
        assert args.network is None or isinstance(args.network, str)
        assert args.token is None or isinstance(args.token, str)
        assert isinstance(args.wait_for_acceptance, bool)

        network_command_util = NetworkCommandUtil(args)
        network_config = network_command_util.get_network_config()
        gateway_client = network_command_util.get_gateway_client()
        signer = get_signer(args, network_config, args.account_address)

        block_explorer = create_block_explorer(
            block_explorer_name=args.block_explorer,
            network=network_config.network_name,
        )

        contract_name = args.contract

        contract_path = self._contract_path_resolver.contract_path_from_contract_name(
            contract_name
        )

        contract_sierra, contract_casm = Cairo1ContractCompiler.compile_contract(
            contract_name=contract_name,
            contract_path=contract_path,
            linked_libraries=fetch_linked_libraries_from_scarb(
                package_root_path=self._contract_path_resolver.project_root_path,
            ),
        )

        response = await self.declare(
            compiled_contract_sierra=contract_sierra,
            compiled_contract_casm=contract_casm,
            signer=signer,
            account_address=args.account_address,
            gateway_client=gateway_client,
            token=args.token,
            wait_for_acceptance=args.wait_for_acceptance,
            max_fee=args.max_fee,
        )

        write(
            SuccessfulDeclareMessage(
                response=response,
                class_url=block_explorer.create_link_to_class(response.class_hash),
                tx_url=block_explorer.create_link_to_transaction(
                    response.transaction_hash
                ),
            )
        )

        return response

    async def declare(
        self,
        compiled_contract_sierra: str,
        compiled_contract_casm: str,
        max_fee: Fee,
        signer: BaseSigner,
        gateway_client: GatewayClient,
        account_address: Address,
        token: Optional[str] = None,
        wait_for_acceptance: bool = False,
    ) -> SuccessfulDeclareResponse:
        gateway_facade = self._gateway_facade_factory.create(gateway_client)
        return await gateway_facade.declare_cairo1(
            compiled_contract_sierra=compiled_contract_sierra,
            compiled_contract_casm=compiled_contract_casm,
            signer=signer,
            account_address=account_address,
            wait_for_acceptance=wait_for_acceptance,
            token=token,
            max_fee=max_fee,
        )
