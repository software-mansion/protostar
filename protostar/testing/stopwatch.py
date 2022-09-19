import time
from contextlib import contextmanager
from copy import deepcopy
from typing import Dict

from typing_extensions import Self


class Stopwatch:
    def __init__(self):
        self.laps: Dict[str, float] = {}

    @contextmanager
    def lap(self, name: str):
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()

            if name in self.laps:
                raise KeyError(f"Lap '{name}' has been already measured.")

            self.laps[name] = end_time - start_time

    @property
    def total_elapsed(self) -> float:
        return sum(self.laps.values())

    def fork(self) -> Self:
        return deepcopy(self)
