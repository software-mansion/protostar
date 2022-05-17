from dataclasses import dataclass
from logging import Logger


@dataclass
class SuccessfulGatewayResponseFacade:
    code: str
    address: int
    transaction_hash: str

    def log(self, logger: Logger):
        logger.info(
            "\n".join(
                [
                    "Deploy transaction was sent.",
                    f"Contract address: 0x{self.address:064x}",
                    f"Transaction hash: {self.transaction_hash}",
                ]
            )
        )
