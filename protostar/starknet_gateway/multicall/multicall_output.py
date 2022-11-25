from dataclasses import dataclass


@dataclass(frozen=True)
class MulticallOutput:
    transaction_hash: int
