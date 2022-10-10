import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, List, Optional, Pattern

from starkware.starknet.utils.api_utils import cast_to_felts

from protostar.starknet_gateway import Fee


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

            @staticmethod
            def felt(arg: str) -> int:
                [output] = cast_to_felts([arg])
                return output

            @staticmethod
            def fee(arg: str) -> Fee:
                if arg == "auto":
                    return arg
                return int(arg)

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
    async def run(self, args: Any) -> Any:
        ...
