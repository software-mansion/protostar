from abc import abstractmethod, ABC

from typing_extensions import Self


class CheaterException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class Cheater(ABC):
    @abstractmethod
    def copy(self) -> Self:
        ...

    @abstractmethod
    def apply(self, parent: Self) -> None:
        ...
