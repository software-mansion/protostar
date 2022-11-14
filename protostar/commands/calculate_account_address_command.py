from argparse import Namespace
from logging import Logger
from typing import Optional

from protostar.cli import ProtostarCommand
from protostar.starknet.account_address import AccountAddress
from protostar.cli.common_arguments import (
    ACCOUNT_CLASS_HASH_ARG,
    ACCOUNT_ADDRESS_SALT_ARG,
    ACCOUNT_CONSTRUCTOR_INPUT,
)


class CalculateAccountAddressCommand(ProtostarCommand):
    def __init__(
        self,
        logger: Logger,
    ) -> None:
        self._logger = logger

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
            ACCOUNT_CLASS_HASH_ARG,
            ACCOUNT_ADDRESS_SALT_ARG,
            ACCOUNT_CONSTRUCTOR_INPUT,
        ]

    async def run(self, args: Namespace):
        account_address = AccountAddress.from_class_hash(
            class_hash=args.account_class_hash,
            constructor_calldata=args.account_constructor_input,
            salt=args.account_address_salt,
        )
        self._logger.info(account_address)
