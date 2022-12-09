import importlib
import os
from typing import Any, Type

from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig
from .protostar_argument import ProtostarArgument

PRIVATE_KEY_ENV_VAR_NAME = "PROTOSTAR_ACCOUNT_PRIVATE_KEY"


class SignableCommandUtil:
    signable_arguments = [
        ProtostarArgument(
            name="account-address",
            description="Account address.",
            type="address",
            is_required=True,
        ),
        ProtostarArgument(
            name="private-key-path",
            description="Path to the file, which stores your private key (in hex representation) for the account. \n"
            f"Can be used instead of {PRIVATE_KEY_ENV_VAR_NAME} env variable.",
            type="path",
        ),
        ProtostarArgument(
            name="signer-class",
            description="Custom signer class module path.",
            type="str",
        ),
    ]

    def __init__(self, args: Any):
        self._args = args

    def get_signer(
        self,
        network_config: NetworkConfig,
    ) -> BaseSigner:
        if self._args.signer_class:
            *module_names, class_name = self._args.signer_class.split(".")
            module = ".".join(module_names)
            signer_module = importlib.import_module(module)
            signer_class = getattr(signer_module, class_name)
            SignableCommandUtil._validate_signer_interface(signer_class)
            return signer_class()

        private_key_str = None
        if self._args.private_key_path:
            with open(self._args.private_key_path, encoding="utf-8") as file:
                private_key_str = file.read()

        if not private_key_str:
            private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)

        if not private_key_str or not self._args.account_address:
            raise ProtostarException(
                "Signing is mandatory, please provide an account and a private key in order to sign transactions."
            )

        private_key_str = private_key_str.strip()
        if not private_key_str.startswith("0x"):
            private_key_str = hex(int(private_key_str))

        try:
            private_key = int(private_key_str, 16)
        except ValueError as v_err:
            raise ProtostarException(
                f"Invalid private key format ({private_key_str}). Please provide hex-encoded number."
            ) from v_err

        key_pair = KeyPair.from_private_key(private_key)

        try:
            signer = StarkCurveSigner(
                account_address=int(self._args.account_address),
                key_pair=key_pair,
                chain_id=network_config.chain_id,
            )
        except ValueError as v_err:
            raise ProtostarException(
                f"Invalid account address format ({self._args.account_address}). "
                "Please provide hex-encoded number."
            ) from v_err

        return signer

    @staticmethod
    def _validate_signer_interface(signer_class: Type):
        if not issubclass(signer_class, BaseSigner):
            raise ProtostarException(
                "Signer class has to extend BaseSigner ABC.\n"
                "Please refer to the starknet.py docs for more information:\n"
                "https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner"
            )
