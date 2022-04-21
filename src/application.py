import argparse
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Any, List, Optional

from attr import dataclass
from typing_extensions import Literal

InputAllowedType = Literal["string", "Path[]", "number", "bool"]


class AbstractCommand(ABC):
    @dataclass
    class Argument:
        name: str
        description: str
        input_type: InputAllowedType
        is_positional: bool
        example: Optional[str]

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
    async def run(self):
        ...


class ArgumentParserFacade:
    def __init__(self, argument_parser: ArgumentParser) -> None:
        self.argument_parser = argument_parser
        self.command_parsers = self.argument_parser.add_subparsers(dest="command")

    def add_command(self, command: AbstractCommand) -> "ArgumentParserFacade":
        self.command_parsers.add_parser(
            command.name,
            formatter_class=argparse.RawTextHelpFormatter,
        )

        return self

    def add_root_argument(
        self, argument: AbstractCommand.Argument
    ) -> "ArgumentParserFacade":
        self.argument_parser.add_argument()
        return self

    def parse(self) -> Any:
        return self.argument_parser.parse_args()


class Application:
    def __init__(
        self, commands: List[AbstractCommand], root_args: List[AbstractCommand.Argument]
    ) -> None:
        self.commands = commands
        self.root_args = root_args

    def setup_parser(
        self, argument_parser: ArgumentParserFacade
    ) -> ArgumentParserFacade:

        for cmd in self.commands:
            argument_parser.add_command(cmd)

        return argument_parser

    def generate_cli_reference_markdown(self) -> str:
        result: List[str] = []

        result += self._generate_args_markdown(self.root_args)

        for command in self.commands:
            result.append(f"## `{command.name}`")
            if command.example:
                result.append(f"```shell\n{command.example}\n```")
            result.append(f"{command.description}")

            result += self._generate_args_markdown(command.arguments)

        return "\n".join(result)

    # pylint: disable=no-self-use
    def _generate_args_markdown(
        self, arguments: List[AbstractCommand.Argument]
    ) -> List[str]:
        result: List[str] = []

        for arg in arguments:
            result.append(f"### `{arg.name}`")
            if arg.example:
                result.append(f"```\n{arg.example}\n```")
            result.append(f"{arg.description}")

        return result
