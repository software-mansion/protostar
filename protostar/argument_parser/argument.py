from dataclasses import dataclass, replace
from typing import Any, Generic, Optional, TypeVar, Dict

from typing_extensions import Self

ArgTypeNameT = TypeVar("ArgTypeNameT")

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

    def copy_with(self, **changes: Any) -> Self:
        return replace(self, **changes)
