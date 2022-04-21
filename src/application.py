import argparse
import re
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List, Optional, Pattern

from attr import dataclass
from typing_extensions import Literal

InputAllowedType = Literal["str", "directory", "path", "bool", "regexp"]


class AbstractCommand(ABC):
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
        input_type: InputAllowedType
        is_required: bool = False
        is_array: bool = False
        default: Optional[str] = None
        example: Optional[str] = None

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
        command_parser = self.command_parsers.add_parser(
            command.name,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        for arg in command.arguments:
            ArgumentParserFacade.add_argument(command_parser, arg)

        return self

    def add_root_argument(
        self, argument: AbstractCommand.Argument
    ) -> "ArgumentParserFacade":
        ArgumentParserFacade.add_argument(self.argument_parser, argument)
        return self

    @staticmethod
    def add_argument(
        argument_parser: ArgumentParser, argument: AbstractCommand.Argument
    ) -> ArgumentParser:
        name = argument.name if argument.is_required else f"--{argument.name}"

        if argument.input_type == "bool":
            assert argument.is_required is False, "Booleans must be always optional"
            assert argument.is_array is False, "Array of booleans is not allowed"
            argument_parser.add_argument(
                name,
                help=argument.description,
                action="store_true",
            )
            return argument_parser

        arg_type = str

        if argument.input_type == "directory":
            arg_type = AbstractCommand.Argument.Type.directory
        elif argument.input_type == "regexp":
            arg_type = AbstractCommand.Argument.Type.regexp
        elif argument.input_type == "path":
            arg_type = Path

        default = arg_type(argument.default) if argument.default and arg_type else None

        if not default and argument.is_array:
            default = []

        nargs = "?"
        if argument.is_array:
            nargs = "+"

        argument_parser.add_argument(
            name,
            type=arg_type,
            default=default,
            nargs=nargs,
            help=argument.description,
        )
        return argument_parser

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
