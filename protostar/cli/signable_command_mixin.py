import importlib
import os
import sys
from typing import List, Any

from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner, KeyPair

from protostar.cli import Command
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig

PRIVATE_KEY_ENV_VAR_NAME = "ACCOUNT_PRIVATE_KEY"


class SignableCommandMixin:
    @staticmethod
    def get_signer(args: Any, network_config: NetworkConfig) -> BaseSigner:
        private_key_str = None

        if args.private_key_path:
            with open(args.private_key_path, encoding="utf-8") as file:
                private_key_str = file.read()

        if not private_key_str:
            private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)

        if not private_key_str:
            raise ProtostarException(
                f"Private key has to be specified either with private-key-path option or {PRIVATE_KEY_ENV_VAR_NAME} "
                "environment variable"
            )

        private_key = int(private_key_str, 16)
        key_pair = KeyPair.from_private_key(private_key)

        signer_args = {
            "account_address": args.account_address,
            "key_pair": key_pair,
            "chain_id": network_config.chain_id,
        }

        signer = None
        if args.pythonpath_ext:
            sys.path.extend(args.pythonpath_ext)
        if args.signer_class:
            *module_names, class_name = args.signer_class.split(".")
            module = ".".join(module_names)
            signer_module = importlib.import_module(module)
            signer_class = getattr(signer_module, class_name)

            signer = signer_class(**signer_args)
        if not signer:
            signer = StarkCurveSigner(**signer_args)

        return signer

    @property
    def signable_arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="account-address",
                description="Account address",
                type="str",
                is_required=True,
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
            Command.Argument(
                name="pythonpath-ext",
                description="PYTHONPATH extensions, for custom code roots registration. You can extend PYTHONPATH with "
                "the same result as well.",
                type="str",
                is_array=True,
            ),
        ]
