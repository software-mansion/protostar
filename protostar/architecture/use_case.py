from abc import abstractmethod
from typing import Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


class UseCase(Generic[Input, Output]):
    @abstractmethod
    async def execute(self, data: Input) -> Output:
        ...
