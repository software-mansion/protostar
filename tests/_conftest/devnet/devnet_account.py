from dataclasses import dataclass

from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

from protostar.starknet import AccountAddress


@dataclass
class DevnetAccount:
    address: AccountAddress
    private_key: str
    public_key: str
    signer: StarkCurveSigner
