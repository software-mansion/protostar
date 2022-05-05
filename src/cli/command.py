import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional, Pattern

from attr import dataclass, frozen
from typing_extensions import Literal

InputAllowedType = Literal["str", "directory", "path", "bool", "regexp"]


@frozen
class Command(ABC):
    @dataclass
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
        default: Optional[str] = None
        example: Optional[str] = None
        short_name: Optional[str] = None

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
