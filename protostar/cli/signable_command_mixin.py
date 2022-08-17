import importlib
import os
from logging import Logger
from typing import List, Any, Optional, cast

from starknet_py.net.models import Transaction, AddressRepresentation, parse_address
from starknet_py.net.models.transaction import Declare, InvokeFunction
from starknet_py.net.signer import BaseSigner

from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.utils.crypto.facade import message_signature
from starkware.starknet.core.os.transaction_hash.transaction_hash import (
    calculate_declare_transaction_hash,
    calculate_transaction_hash_common,
    TransactionHashPrefix,
)
from starkware.starknet.definitions.transaction_type import TransactionType

from protostar.cli import Command

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig

PRIVATE_KEY_ENV_VAR_NAME = "ACCOUNT_PRIVATE_KEY"


class PatchedStarkCurveSigner(BaseSigner):
    def __init__(
        self, account_address: AddressRepresentation, key_pair: KeyPair, chain_id: int
    ):
        self.address = parse_address(account_address)
        self.key_pair = key_pair
        self.chain_id = chain_id

    @property
    def private_key(self) -> int:
        return self.key_pair.private_key

    @property
    def public_key(self) -> int:
        return self.key_pair.public_key

    def sign_transaction(
        self,
        transaction: Transaction,
    ) -> List[int]:
        if transaction.tx_type == TransactionType.DECLARE:
            transaction = cast(Declare, transaction)

            tx_hash = calculate_declare_transaction_hash(
                contract_class=transaction.contract_class,
                chain_id=self.chain_id,
                sender_address=self.address,
                max_fee=transaction.max_fee,
                version=transaction.version,
            )
        else:
            transaction = cast(InvokeFunction, transaction)
            tx_hash = calculate_transaction_hash_common(
                tx_hash_prefix=TransactionHashPrefix.INVOKE,
                version=transaction.version,
                contract_address=self.address,
                entry_point_selector=transaction.entry_point_selector,
                calldata=transaction.calldata,
                max_fee=transaction.max_fee,
                chain_id=self.chain_id,
                additional_data=[],
            )
            # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=self.private_key)
        return [r, s]


class SignableCommandMixin:
    @staticmethod
    def get_signer(
        args: Any,
        network_config: NetworkConfig,
        logger: Logger,
    ) -> Optional[
        BaseSigner
    ]:  # TODO(arcticae): Make it non-optional in some time in the future
        if args.signer_class:
            *module_names, class_name = args.signer_class.split(".")
            module = ".".join(module_names)
            signer_module = importlib.import_module(module)
            signer_class = getattr(signer_module, class_name)
            SignableCommandMixin._validate_signer_interface(signer_class)
            return signer_class()

        private_key_str = None
        if args.private_key_path:
            with open(args.private_key_path, encoding="utf-8") as file:
                private_key_str = file.read()

        if args.private_key_path and not args.account_address:
            raise ProtostarException(
                "account-address option has to be specified when using private key for signing"
            )

        if not private_key_str:
            private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)

        if args.account_address and not private_key_str:
            raise ProtostarException(
                f"Private key has to be specified either with private-key-path option or {PRIVATE_KEY_ENV_VAR_NAME} "
                "environment variable"
            )

        if (
            not private_key_str or not args.account_address
        ):  # FIXME(arcticae): This is temporary, when the signing is mandatory this should be removed
            logger.warning(
                "Signing declare transactions will be mandatory in future versions, please refer to the docs for "
                "more details "
            )
            return None

        try:
            private_key = int(private_key_str, 16)
        except ValueError as v_err:
            raise ProtostarException(
                f"Invalid private key format ({private_key_str}). Please provide hex-encoded number."
            ) from v_err

        key_pair = KeyPair.from_private_key(private_key)

        try:
            signer = PatchedStarkCurveSigner(
                account_address=args.account_address,
                key_pair=key_pair,
                chain_id=network_config.chain_id,
            )  # FIXME(arcticae): Change the default signer to starknet.py one, on 0.10 support
        except ValueError as v_err:
            raise ProtostarException(
                f"Invalid account address format ({args.account_address}). Please provide hex-encoded number."
            ) from v_err

        return signer

    @staticmethod
    def _validate_signer_interface(signer_class):
        if not issubclass(signer_class, BaseSigner):
            raise ProtostarException(
                "Signer class has to extend BaseSigner ABC.\n"
                "Please refer to the starknet.py docs for more information:\n"
                "https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner"
            )

    @property
    def signable_arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="account-address",
                description="Account address",
                type="str",
            ),
            Command.Argument(
                name="private-key-path",
                description="File which stores your private key (in hex representation) for the account. Value is "
                f"omitted if {PRIVATE_KEY_ENV_VAR_NAME} env variable is defined, in which case it's used as the "
                "private key.",
                type="path",
            ),
            Command.Argument(
                name="signer-class",
                description="Custom signer class module path.",
                type="str",
            ),
        ]
