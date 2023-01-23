from dataclasses import dataclass


@dataclass
class CheaterException(Exception):
    message: str
    raw_ex: Exception
