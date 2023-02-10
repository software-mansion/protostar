from dataclasses import dataclass
from typing import Union

from starkware.starknet.public.abi import get_selector_from_name


@dataclass
class Selector:
    def __init__(self, value: Union[str, int]) -> None:
        self._value = value

    def __int__(self) -> int:
        if isinstance(self._value, int):
            return self._value
        return get_selector_from_name(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Selector):
            return int(self) == int(__o)
        return False

    def __hash__(self) -> int:
        return hash(self._value)
