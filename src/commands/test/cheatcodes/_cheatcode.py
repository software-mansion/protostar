from abc import ABC, abstractmethod
from typing import Callable


class Cheatcode(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def build(self) -> Callable:
        ...
