from abc import ABC, abstractmethod
from typing import Any, List, Optional

from protostar.cli.arg_type import ArgTypeName

from .argument import Argument


class Command(ABC):
    Argument = Argument[ArgTypeName]

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def example(self) -> Optional[str]:
        ...

    @property
    @abstractmethod
    def arguments(self) -> List[Argument]:
        ...

    @abstractmethod
    async def run(self, args: Any) -> Any:
        ...
