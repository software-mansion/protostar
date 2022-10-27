from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SuccessfulDeployResponse:
    code: str
    address: int
    transaction_hash: int


def format_successful_deploy_response(
    response: SuccessfulDeployResponse, extra_msg: Optional[List[str]] = None
):
    return "\n".join(
        [
            "Deploy transaction was sent.",
            f"Contract address: 0x{response.address:064x}",
            f"Transaction hash: 0x{response.transaction_hash:064x}",
        ]
        + (extra_msg or [])
    )


@dataclass
class SuccessfulDeclareResponse:
    code: str
    class_hash: int
    transaction_hash: int


def format_successful_declare_response(
    response: SuccessfulDeclareResponse, extra_msg: Optional[List[str]] = None
):
    return "\n".join(
        [
            "Declare transaction was sent.",
            f"Class hash: 0x{response.class_hash:064x}",
            f"Transaction hash: 0x{response.transaction_hash:064x}",
        ]
        + (extra_msg or [])
    )


@dataclass
class SuccessfulInvokeResponse:
    transaction_hash: int


@dataclass
class SuccessfulDeployAccountResponse:
    address: int
    transaction_hash: int
    code: str
