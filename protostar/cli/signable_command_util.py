import importlib
import os
from pathlib import Path
from typing import Optional

from attr import dataclass
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.cli import Command
from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig

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


def create_signer_config_from_args(args):
    return SignerConfig(
        account_address=args.account_address,
        signer_class_module_path=args.signer_class_module_path,
        private_key=get_private_key(args.private_key_path),
    )


def get_private_key(private_key_path: Optional[Path]) -> Optional[int]:
    private_key_str: Optional[str] = None
    if private_key_path:
        private_key_str = private_key_path.read_text()
    if not private_key_str:
        private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)
    if not private_key_str:
        return None
    try:
        return int(private_key_str, base=16)
    except ValueError as v_err:
        raise ProtostarException(
            f"Invalid private key format ({private_key_str}). Please provide hex-encoded number."
        ) from v_err


@dataclass
class SignerConfig:
    account_address: Optional[str]
    private_key: Optional[int]
    signer_class_module_path: Optional[str]


class SignerFactory:
    def create_signer(
        self,
        network_config: NetworkConfig,
        account_config: SignerConfig,
    ) -> Optional[BaseSigner]:
        if account_config.signer_class_module_path:
            return self._create_custom_signer(
                signer_class_path=account_config.signer_class_module_path
            )
        return self._create_default_signer(network_config, account_config)

    @staticmethod
    def _create_custom_signer(signer_class_path: str) -> BaseSigner:
        *module_names, class_name = signer_class_path.split(".")
        module = ".".join(module_names)
        signer_module = importlib.import_module(module)
        # pylint: disable=invalid-name
        SignerClass = getattr(signer_module, class_name)
        if not issubclass(SignerClass, BaseSigner):
            raise UnknownSignerClassException()
        return SignerClass()

    def _create_default_signer(
        self,
        network_config: NetworkConfig,
        account_config: SignerConfig,
    ) -> StarkCurveSigner:
        if not account_config.private_key or not account_config.account_address:
            raise SigningCredentialsNotFound()
        key_pair = KeyPair.from_private_key(account_config.private_key)
        try:
            signer = StarkCurveSigner(
                account_address=account_config.account_address,
                key_pair=key_pair,
                chain_id=network_config.chain_id,
            )
        except ValueError as v_err:
            raise ProtostarException(
                f"Invalid account address format ({account_config.account_address}). "
                "Please provide hex-encoded number."
            ) from v_err
        return signer


class SigningCredentialsNotFound(ProtostarException):
    def __init__(self):
        super().__init__(
            "Signing credentials not found. "
            "Signing transactions will be mandatory in future versions, "
            "please refer to the docs for more details:\n"
            "https://docs.swmansion.com/protostar/docs/tutorials/deploying/cli#signing-a-declaration"
        )


class UnknownSignerClassException(ProtostarException):
    def __init__(self):
        super().__init__(
            "Signer class has to extend BaseSigner ABC.\n"
            "Please refer to the starknet.py docs for more information:\n"
            "https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner"
        )
