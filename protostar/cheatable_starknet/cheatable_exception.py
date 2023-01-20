from dataclasses import dataclass


@dataclass
class CheatableException(Exception):
    message: str
