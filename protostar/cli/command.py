import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, List, Optional, Pattern

from typing_extensions import Literal

InputAllowedType = Literal[
    "str",
    "directory",
    "path",
    "bool",
    "regexp",
    "int",
]


class Command(ABC):

    # pylint: disable=too-many-instance-attributes
    @dataclass(frozen=True)
    class Argument:
        class Type:
            @staticmethod
            def regexp(arg: str) -> Pattern:
                return re.compile(arg)

            @staticmethod
            def directory(arg: str) -> Path:
                pth = Path(arg)
                assert pth.is_dir(), f'"{str(pth)}" is not a valid directory path'
                return pth

        name: str
        description: str
        type: InputAllowedType
        is_positional: bool = False
        is_required: bool = False
        is_array: bool = False
        default: Any = None
        example: Optional[str] = None
        short_name: Optional[str] = None

        def copy_with(self, **changes) -> "Command.Argument":
            return replace(self, **changes)

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
    async def run(self, args: Any):
        ...
