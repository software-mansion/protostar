from dataclasses import dataclass

from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.protostar_exception import ProtostarException


@dataclass
class AccountConfig:
    account_address: str
    signer: BaseSigner


def create_stark_curve_signer(
    account_address: str,
    private_key: int,
    chain_id: StarknetChainId,
) -> StarkCurveSigner:
    key_pair = KeyPair.from_private_key(private_key)
    try:
        signer = StarkCurveSigner(
            account_address=account_address,
            key_pair=key_pair,
            chain_id=chain_id,
        )
    except ValueError as v_err:
        raise ProtostarException(
            f"Invalid account address format ({account_address}). "
            "Please provide hex-encoded number."
        ) from v_err
    return signer
