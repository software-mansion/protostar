from typing import Any, Callable, Generic, Literal, Protocol, TypeVar

ArgTypeName = Literal[
    "str",
    "directory",
    "path",
    "bool",
    "regexp",
    "int",
]

ArgTypeNameT_contra = TypeVar(
    "ArgTypeNameT_contra", contravariant=True, bound=ArgTypeName
)


class ParserFactoryProtocol(Protocol, Generic[ArgTypeNameT_contra]):
    def create(self, argument_type: ArgTypeNameT_contra) -> Callable[[str], Any]:
        ...
