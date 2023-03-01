from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Union

T = TypeVar("T")


Offset = int
OffsetOrName = Union[str, Offset]


class CairoFunctionExecutor(ABC, Generic[T]):
    @abstractmethod
    async def execute(self, function_identifier: OffsetOrName) -> T:
        ...
