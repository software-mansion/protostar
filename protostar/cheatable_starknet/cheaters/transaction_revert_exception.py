from dataclasses import dataclass


@dataclass
class TransactionRevertException(Exception):
    message: str
    raw_ex: Exception
