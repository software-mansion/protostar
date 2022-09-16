import os
from typing import Optional

Seed = int


def determine_testing_seed(seed: Optional[Seed]) -> Seed:

    return seed or random_seed()


def random_seed() -> Seed:
    return int.from_bytes(os.urandom(4), byteorder="little", signed=False)
