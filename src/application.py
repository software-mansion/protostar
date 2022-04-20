from abc import ABC, abstractmethod
from typing import List, Optional

from attr import dataclass
from typing_extensions import Literal

InputAllowedType = Literal["string", "Path[]", "number", "bool"]


@dataclass
class Argument:
    name: str
    description: str
    input_type: InputAllowedType
    is_positional: bool
    example: Optional[str]


class AbstractCommand(ABC):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def example(self) -> Optional[str]:
        ...

    def __init__(self, arguments: List[Argument]) -> None:
        super().__init__()

        self.arguments = arguments

    @abstractmethod
    def run(self):
        ...


class Application:
    def __init__(self, inputs: List[Argument | AbstractCommand]) -> None:
        pass
