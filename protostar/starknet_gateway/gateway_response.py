from dataclasses import dataclass
from logging import Logger
from typing import List, Optional


@dataclass
class SuccessfulDeployResponse:
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


@dataclass
class SuccessfulDeclareResponse:
    code: str
    class_hash: int
    transaction_hash: str

    def log(self, logger: Logger, extra_msg: Optional[List[str]] = None):
        logger.info(
            "\n".join(
                [
                    "Declare transaction was sent.",
                    f"Class hash: 0x{self.class_hash:064x}",
                    f"Transaction hash: {self.transaction_hash}",
                ]
                + (extra_msg or [])
            )
        )
