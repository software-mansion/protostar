from abc import abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

from protostar.cli.arg_type import ArgTypeName

from .arg_type import ArgTypeName
from .argument import Argument as GenericArgument

ArgTypeNameT_co = TypeVar("ArgTypeNameT_co", covariant=True)


class Command(Generic[ArgTypeNameT_co]):
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
    def arguments(self) -> List[GenericArgument[ArgTypeNameT_co]]:
        ...

    @abstractmethod
    async def run(self, args: Any) -> Any:
        ...
