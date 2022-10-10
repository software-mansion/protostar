from dataclasses import dataclass, replace
from typing import Any, Generic, Optional, TypeVar

from .arg_type import ArgTypeName

ArgTypeNameT = TypeVar("ArgTypeNameT", bound=ArgTypeName)

# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Argument(Generic[ArgTypeNameT]):
    name: str
    description: str
    type: ArgTypeNameT
    is_positional: bool = False
    is_required: bool = False
    is_array: bool = False
    default: Any = None
    example: Optional[str] = None
    short_name: Optional[str] = None

    def copy_with(self, **changes) -> "Argument":
        return replace(self, **changes)
