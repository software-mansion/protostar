from abc import abstractmethod
from argparse import Namespace
from typing import Any, Generic, List, Optional, TypeVar

from .argument import Argument as GenericArgument

ArgTypeNameT_co = TypeVar("ArgTypeNameT_co", covariant=True)
ArgType = TypeVar("ArgType", bound=GenericArgument)


class Command(Generic[ArgType]):
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
    def arguments(self) -> List[ArgType]:
        ...

    @abstractmethod
    async def run(self, args: Namespace) -> Any:
        ...
