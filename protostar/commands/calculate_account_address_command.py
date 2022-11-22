from argparse import Namespace
from typing import Optional

from protostar.cli import ProtostarCommand, MessengerFactory
from protostar.io import LogColorProvider, StructuredMessage
from protostar.starknet import Address
from protostar.cli.common_arguments import (
    ACCOUNT_CLASS_HASH_ARG,
    ACCOUNT_ADDRESS_SALT_ARG,
    ACCOUNT_CONSTRUCTOR_INPUT,
)


class AccountAddressMessage(StructuredMessage):
    def __init__(self, account_address: Address) -> None:
        super().__init__()
        self._account_address = account_address

    def format_human(self, fmt: LogColorProvider) -> str:
        return f"Address: {self._account_address}"

    def format_dict(self) -> dict:
        return {"address": str(self._account_address)}


class CalculateAccountAddressCommand(ProtostarCommand):
    def __init__(self, messenger_factory: MessengerFactory):
        self._messenger_factory = messenger_factory

    @property
    def name(self) -> str:
        return "calculate-account-address"

    @property
    def description(self) -> str:
        return (
            "In order to create an account, you need to prefund the account. "
            "To prefund the account you need to know its address. "
            "This command calculates the account address."
        )

    @property
    def example(self) -> Optional[str]:
        return None

    @property
    def arguments(self):
        return [
            *MessengerFactory.OUTPUT_ARGUMENTS,
            ACCOUNT_CLASS_HASH_ARG,
            ACCOUNT_ADDRESS_SALT_ARG,
            ACCOUNT_CONSTRUCTOR_INPUT,
        ]

    async def run(self, args: Namespace):
        write = self._messenger_factory.from_args(args)
        account_address = Address.from_class_hash(
            class_hash=args.account_class_hash,
            constructor_calldata=args.account_constructor_input,
            salt=args.account_address_salt,
        )
        write(AccountAddressMessage(account_address))
        return account_address
