import os
from contextvars import ContextVar, Token
from dataclasses import dataclass, field, InitVar
from multiprocessing import Value
from typing import Optional

from typing_extensions import Self

Seed = int
_testing_seed: ContextVar["TestingSeed"] = ContextVar("testing_seed")


@dataclass
class TestingSeed:
    seed: InitVar[Optional[Seed]] = None

    value: Seed = field(init=False)

    _was_used: Value = field(default_factory=lambda: Value("B", 0), init=False)  # type: ignore
    _token: Optional[Token] = field(default=None, init=False)

    def __post_init__(self, seed: Optional[Seed]):
        self.value = seed or random_seed()

    @staticmethod
    def current() -> Seed:
        self = _testing_seed.get()

        # pylint: disable=protected-access
        self._set_used()

        return self.value

    @property
    def was_used(self) -> bool:
        return self._was_used.value != 0

    def _set_used(self):
        with self._was_used.get_lock():
            self._was_used.value = 1

    def __enter__(self) -> Self:
        assert self._token is None
        assert _testing_seed.get(None) is None, f"{type(self)} usage cannot be nested."
        self._token = _testing_seed.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._token is not None
        _testing_seed.reset(self._token)
        self._token = None


def random_seed() -> Seed:
    return int.from_bytes(os.urandom(4), byteorder="little", signed=False)
