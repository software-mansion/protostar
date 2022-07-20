import os
from contextvars import ContextVar, Token
from dataclasses import dataclass, field, InitVar
from typing import Optional

Seed = int
_testing_seed: ContextVar["TestingSeed"] = ContextVar("testing_seed")


@dataclass
class TestingSeed:
    seed: InitVar[Optional[Seed]] = None

    _value: Seed = field(init=False)
    _used: bool = field(default=False, init=False)
    _token: Optional[Token] = field(default=None, init=False)

    def __post_init__(self, seed: Optional[Seed]):
        self._value = seed or random_seed()

    @staticmethod
    def current() -> Seed:
        self = _testing_seed.get()

        # pylint: disable=protected-access
        self._used = True
        return self._value

    @staticmethod
    def was_used() -> bool:
        self = _testing_seed.get()

        # pylint: disable=protected-access
        return self._used

    def __enter__(self):
        self._token = _testing_seed.set(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._token is not None
        _testing_seed.reset(self._token)


def random_seed() -> Seed:
    return int.from_bytes(os.urandom(4), byteorder="little", signed=False)
