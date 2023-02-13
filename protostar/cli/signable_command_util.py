import importlib
import os
from typing import Any, Optional, Type

from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.protostar_exception import ProtostarException
from protostar.starknet_gateway import NetworkConfig
from protostar.starknet import Address
from protostar.cli.common_arguments import PRIVATE_KEY_ENV_VAR_NAME


def get_signer(
    _args: Any,
    network_config: NetworkConfig,
    optional_account_address: Optional[Address] = None,
) -> BaseSigner:
    if _args.signer_class:
        *module_names, class_name = _args.signer_class.split(".")
        module = ".".join(module_names)
        signer_module = importlib.import_module(module)
        signer_class = getattr(signer_module, class_name)
        _validate_signer_interface(signer_class)
        return signer_class()

    private_key_str = None
    if _args.private_key_path:
        with open(_args.private_key_path, encoding="utf-8") as file:
            private_key_str = file.read()

    if not private_key_str:
        private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)

    if not private_key_str:
        raise ProtostarException(
            "Signing is mandatory, please provide a private key in order to sign transactions."
        )

    try:
        private_key_str = private_key_str.strip()
        if not private_key_str.startswith("0x"):
            private_key_str = hex(int(private_key_str))
        private_key = int(private_key_str, 16)
    except ValueError as v_err:
        raise ProtostarException(
            f"Invalid private key format ({private_key_str}). Please provide hex-encoded number."
        ) from v_err

    key_pair = KeyPair.from_private_key(private_key)

    account_address = (
        _args.account_address
        if hasattr(_args, "account_address")
        else optional_account_address
    )
    assert account_address is not None

    try:
        signer = StarkCurveSigner(
            account_address=int(account_address),
            key_pair=key_pair,
            chain_id=network_config.chain_id,
        )
    except ValueError as v_err:
        raise ProtostarException(
            f"Invalid account address format ({_args.account_address}). "
            "Please provide hex-encoded number."
        ) from v_err

    return signer


def _validate_signer_interface(signer_class: Type):
    if not issubclass(signer_class, BaseSigner):
        raise ProtostarException(
            "Signer class has to extend BaseSigner ABC.\n"
            "Please refer to the starknet.py docs for more information:\n"
            "https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner"
        )
