from abc import abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

from protostar.cli.arg_type import ArgTypeName

from .arg_type import ArgTypeName
from .argument import Argument as GenericArgument

ArgTypeNameT = TypeVar("ArgTypeNameT", bound=ArgTypeName)


class Command(Generic[ArgTypeNameT]):
    Argument = GenericArgument[ArgTypeName]

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
    def arguments(self) -> List[GenericArgument[ArgTypeNameT]]:
        ...

    @abstractmethod
    async def run(self, args: Any) -> Any:
        ...
