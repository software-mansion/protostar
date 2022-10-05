from dataclasses import dataclass
from typing import Optional

from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer import BaseSigner
from starknet_py.net.signer.stark_curve_signer import KeyPair, StarkCurveSigner

from protostar.protostar_exception import ProtostarException

ProtostarBaseSigner = BaseSigner
ProtostarDefaultSigner = StarkCurveSigner


@dataclass
class AccountConfig:
    account_address: str
    signer: Optional[ProtostarBaseSigner]


def create_protostar_default_signer(
    account_address: str,
    private_key: int,
    chain_id: StarknetChainId,
) -> ProtostarDefaultSigner:
    key_pair = KeyPair.from_private_key(private_key)
    try:
        signer = ProtostarDefaultSigner(
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
