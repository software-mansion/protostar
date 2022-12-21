from dataclasses import dataclass
from typing import Optional

from protostar.io.log_color_provider import LogColorProvider
from protostar.io.output import StructuredMessage
from protostar.starknet_gateway.invoke import InvokeOutput


class SendingInvokeTransactionMessage(StructuredMessage):
    def format_human(self, fmt: LogColorProvider) -> str:
        return "Sending invoke transaction..."

    def format_dict(self) -> dict:
        return {
            "type": "SENDING_INVOKE_TRANSACTION",
        }


@dataclass
class InvokeTransactionSentMessage(StructuredMessage):
    response: InvokeOutput
    tx_url: Optional[str]

    def format_human(self, fmt: LogColorProvider) -> str:
        lines: list[str] = []
        lines.append("Invoke transaction was sent.")
        tx_hash = f"0x{self.response.transaction_hash:064x}"
        lines.append(f"Transaction hash: {fmt.bold(tx_hash)}")
        if self.tx_url:
            lines.append(self.tx_url)
        return "\n".join(lines)

    def format_dict(self) -> dict:
        return {
            "type": "INVOKE_TRANSACTION_SENT",
            "transaction_hash": f"0x{self.response.transaction_hash:064x}",
        }


class WaitingForAcceptanceMessage(StructuredMessage):
    def format_human(self, fmt: LogColorProvider) -> str:
        return "Waiting for acceptance..."

    def format_dict(self) -> dict:
        return {
            "type": "WAITING_FOR_ACCEPTANCE",
        }


class TransactionAcceptedOnL2Message(StructuredMessage):
    def format_human(self, fmt: LogColorProvider) -> str:
        return "Transaction accepted on L2."

    def format_dict(self) -> dict:
        return {
            "type": "TRANSACTION_ACCEPTED_ON_L2",
        }
