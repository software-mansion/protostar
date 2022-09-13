from abc import abstractmethod, ABC

from typing_extensions import Self


class Cheater(ABC):
    @abstractmethod
    def copy(self) -> Self:
        ...

    @abstractmethod
    def apply(self, parent: Self) -> None:
        ...
