from abc import abstractmethod
from typing import Any, Generic, List, Optional, TypeVar, Union

from protostar.cli.arg_type import ArgTypeName

from .arg_type import ArgTypeName
from .argument import Argument as GenericArgument

ArgTypeNameT = TypeVar("ArgTypeNameT", covariant=True)


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
    def arguments(self) -> List[Union[Argument, GenericArgument[ArgTypeNameT]]]:
        ...

    @abstractmethod
    async def run(self, args: Any) -> Any:
        ...
