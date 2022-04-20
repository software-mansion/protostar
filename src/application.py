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

    def __init__(self, arguments: List[Argument]) -> None:
        super().__init__()

        self.arguments = arguments

    @abstractmethod
    async def run(self):
        ...


class Application:
    def __init__(
        self, commands: List[AbstractCommand], root_args: List[Argument]
    ) -> None:
        self.commands = commands
        self.root_args = root_args

    def generate_cli_reference_markdown(self) -> str:
        result = []

        for arg in self.root_args:
            result.append(f"### `{arg.name}`")
            if arg.example:
                result.append(f"```\n{arg.example}\n```")
            result.append(f"{arg.description}")

        for command in self.commands:
            result.append(f"## `{command.name}`")
            if command.example:
                result.append(f"```shell\n{command.example}\n```")
            result.append(f"{command.description}")

        return "\n".join(result)
