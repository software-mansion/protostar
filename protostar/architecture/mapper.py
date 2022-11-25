from abc import abstractmethod
from typing import Generic, TypeVar

From = TypeVar("From")
To = TypeVar("To")


class Mapper(Generic[From, To]):
    @abstractmethod
    async def map(self, item: From) -> To:
        ...
