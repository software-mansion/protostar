import importlib
import os
from pathlib import Path
from typing import Optional

from starknet_py.net.models import StarknetChainId

from protostar.cli import Command
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import (
    AccountConfig,
    ProtostarBaseSigner,
    create_protostar_default_signer,
)

PRIVATE_KEY_ENV_VAR_NAME = "PROTOSTAR_ACCOUNT_PRIVATE_KEY"


SIGNABLE_ARGUMENTS = [
    Command.Argument(
        name="account-address",
        description="Account address",
        type="str",
    ),
    Command.Argument(
        name="private-key-path",
        description="Path to the file, which stores your private key (in hex representation) for the account. \n"
        f"Can be used instead of {PRIVATE_KEY_ENV_VAR_NAME} env variable.",
        type="path",
    ),
    Command.Argument(
        name="signer-class",
        description="Custom signer class module path.",
        type="str",
    ),
]


def create_account_config_from_args(args, chain_id: StarknetChainId) -> AccountConfig:
    custom_signer: Optional[ProtostarBaseSigner] = None
    if args.signer_class_module_path:
        custom_signer = create_custom_signer(args.signer_class_module_path)
        return AccountConfig(
            account_address=args.account_address, signer_class=custom_signer
        )
    return AccountConfig(
        account_address=args.account_address,
        signer_class=create_protostar_default_signer(
            account_address=args.account_address,
            private_key=get_private_key(args.private_key_path),
            chain_id=chain_id,
        ),
    )


def create_custom_signer(signer_class_path: str) -> ProtostarBaseSigner:
    *module_names, class_name = signer_class_path.split(".")
    module = ".".join(module_names)
    signer_module = importlib.import_module(module)
    # pylint: disable=invalid-name
    SignerClass = getattr(signer_module, class_name)
    if not issubclass(SignerClass, ProtostarBaseSigner):
        raise InvalidSignerClassException()
    return SignerClass()


def get_private_key(private_key_path: Optional[Path]) -> int:
    private_key_str: Optional[str] = None
    if private_key_path:
        private_key_str = private_key_path.read_text()
    if not private_key_str:
        private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)
    if not private_key_str:
        raise SigningCredentialsNotFound()
    try:
        return int(private_key_str, base=16)
    except ValueError as v_err:
        raise ProtostarException(
            f"Invalid private key format ({private_key_str}). Please provide hex-encoded number."
        ) from v_err


class SigningCredentialsNotFound(ProtostarException):
    def __init__(self):
        super().__init__(
            "Signing credentials not found. "
            "Signing transactions will be mandatory in future versions, "
            "please refer to the docs for more details:\n"
            "https://docs.swmansion.com/protostar/docs/tutorials/deploying/cli#signing-a-declaration"
        )


class InvalidSignerClassException(ProtostarException):
    def __init__(self):
        super().__init__(
            "Signer class has to extend BaseSigner ABC.\n"
            "Please refer to the starknet.py docs for more information:\n"
            "https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner"
        )
