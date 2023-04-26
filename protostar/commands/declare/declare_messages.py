from dataclasses import dataclass
from typing import Optional

from protostar.io import StructuredMessage, LogColorProvider
from protostar.starknet_gateway import SuccessfulDeclareResponse


@dataclass
class SuccessfulDeclareMessage(StructuredMessage):
    response: SuccessfulDeclareResponse
    class_url: Optional[str]
    tx_url: Optional[str]

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = []
        lines.append("Declare transaction was sent.")
        lines.append(f"Class hash: 0x{self.response.class_hash:064x}")
        if self.class_url:
            lines.append(self.class_url)
            lines.append("")
        lines.append(f"Transaction hash: 0x{self.response.transaction_hash:064x}")
        if self.tx_url:
            lines.append(self.tx_url)
        return "\n".join(lines)

    def format_dict(self) -> dict:
        return {
            "class_hash": f"0x{self.response.class_hash:064x}",
            "transaction_hash": f"0x{self.response.transaction_hash:064x}",
        }
