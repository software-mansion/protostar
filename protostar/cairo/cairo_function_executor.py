from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class CairoFunctionExecutor(ABC, Generic[T]):
    @abstractmethod
    async def execute(self, function_name: str) -> T:
        ...
