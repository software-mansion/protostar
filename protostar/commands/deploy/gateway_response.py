from dataclasses import dataclass
from logging import Logger
from typing import List, Optional


@dataclass
class SuccessfulGatewayResponse:
    code: str
    address: int
    transaction_hash: str

    def log(self, logger: Logger, extra_msg: Optional[List[str]] = None):
        logger.info(
            "\n".join(
                [
                    "Deploy transaction was sent.",
                    f"Contract address: 0x{self.address:064x}",
                    f"Transaction hash: {self.transaction_hash}",
                ]
                + (extra_msg or [])
            )
        )
