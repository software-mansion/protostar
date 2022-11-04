from dataclasses import dataclass

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner


@dataclass
class DevnetAccount:
    address: str
    private_key: str
    public_key: str
    signer: StarkCurveSigner
