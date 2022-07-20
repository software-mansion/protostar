import os
from contextvars import ContextVar, Token
from dataclasses import dataclass, field, InitVar
from typing import Optional

from typing_extensions import Self

Seed = int
_testing_seed: ContextVar["TestingSeed"] = ContextVar("testing_seed")


@dataclass
class TestingSeed:
    seed: InitVar[Optional[Seed]] = None

    value: Seed = field(init=False)
    was_used: bool = field(default=False, init=False)
    _token: Optional[Token] = field(default=None, init=False)

    def __post_init__(self, seed: Optional[Seed]):
        self.value = seed or random_seed()

    @staticmethod
    def current() -> Seed:
        self = _testing_seed.get()

        # pylint: disable=protected-access
        self.was_used = True
        return self.value

    def __enter__(self) -> Self:
        self._token = _testing_seed.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._token is not None
        _testing_seed.reset(self._token)


def random_seed() -> Seed:
    return int.from_bytes(os.urandom(4), byteorder="little", signed=False)
