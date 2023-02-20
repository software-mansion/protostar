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
    args: Any,
    network_config: NetworkConfig,
    account_address: Optional[Address],
) -> BaseSigner:
    if args.signer_class:
        *module_names, class_name = args.signer_class.split(".")
        module = ".".join(module_names)
        signer_module = importlib.import_module(module)
        signer_class = getattr(signer_module, class_name)
        _validate_signer_interface(signer_class)
        return signer_class()

    private_key_str = None
    if args.private_key_path:
        with open(args.private_key_path, encoding="utf-8") as file:
            private_key_str = file.read()

    if not private_key_str:
        private_key_str = os.environ.get(PRIVATE_KEY_ENV_VAR_NAME)

    if not private_key_str or not account_address:
        raise ProtostarException(
            "Signing is mandatory, please provide an account a private key in order to sign transactions."
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

    try:
        key_pair = KeyPair.from_private_key(private_key)
    except AssertionError as a_err:
        raise ProtostarException(
            "Invalid private key value. Please provide valid private key."
        ) from a_err

    try:
        signer = StarkCurveSigner(
            account_address=int(account_address),
            key_pair=key_pair,
            chain_id=network_config.chain_id,
        )
    except ValueError as v_err:
        raise ProtostarException(
            f"Invalid account address format ({account_address}). "
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
