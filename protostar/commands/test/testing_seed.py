import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Optional

Seed = int
_testing_seed: ContextVar[Seed] = ContextVar("testing_seed")


@contextmanager
def testing_seed(seed: Optional[Seed] = None) -> Iterator[Seed]:
    if seed is None:
        seed = int.from_bytes(os.urandom(4), byteorder="little", signed=False)

    # HACK: Keep typechecker happy
    assert seed is not None

    token = _testing_seed.set(seed)
    try:
        yield seed
    finally:
        _testing_seed.reset(token)


def current_testing_seed() -> Seed:
    return _testing_seed.get()
