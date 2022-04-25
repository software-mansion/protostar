import argparse
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, Sequence

from src.core.cli import CLI
from src.core.command import Command


class ArgumentDefaultValueProvider(ABC):
    @abstractmethod
    def get_default_value(
        self, command: Optional[Command], argument: Command.Argument
    ) -> Optional[Any]:
        ...


class ArgumentParserFacade:
    def __init__(
        self,
        argument_parser: ArgumentParser,
        cli: CLI,
        default_value_provider: Optional[ArgumentDefaultValueProvider] = None,
    ) -> None:
        self.argument_parser = argument_parser
        self.command_parsers = self.argument_parser.add_subparsers(dest="command")
        self.cli = cli
        self._default_value_provider = default_value_provider

        self._setup_parser()

    def parse(self, input_args: Optional[Sequence[str]] = None) -> Any:
        return self.argument_parser.parse_args(input_args)

    def _setup_parser(self) -> None:
        for cmd in self.cli.commands:
            self._add_command(cmd)

        for root_arg in self.cli.root_args:
            self._add_root_argument(root_arg)

    def _add_command(self, command: Command) -> "ArgumentParserFacade":
        command_parser = self.command_parsers.add_parser(
            command.name,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        for arg in command.arguments:
            self._update_arg_default_value_if_necessary(command, arg)
            ArgumentParserFacade._add_argument(command_parser, arg)

        return self

    def _add_root_argument(self, argument: Command.Argument) -> "ArgumentParserFacade":
        assert (
            argument.is_required is False
        ), f"A root argument ({argument.name}) cannot be required"

        self._update_arg_default_value_if_necessary(None, argument)
        ArgumentParserFacade._add_argument(self.argument_parser, argument)
        return self

    def _update_arg_default_value_if_necessary(
        self, command: Optional[Command], argument: Command.Argument
    ) -> Command.Argument:
        if self._default_value_provider:
            new_default = self._default_value_provider.get_default_value(
                command, argument
            )
            if new_default is not None:
                argument.default = new_default
        return argument

    @staticmethod
    def _add_argument(
        argument_parser: ArgumentParser, argument: Command.Argument
    ) -> ArgumentParser:
        name = argument.name if argument.is_required else f"--{argument.name}"
        short_name = f"-{argument.short_name}" if argument.short_name else None

        names = [name]
        if short_name:
            names.append(short_name)

        if argument.type == "bool":
            assert argument.is_required is False, "Booleans must be always optional"
            assert argument.is_array is False, "Array of booleans is not allowed"
            argument_parser.add_argument(
                *names,
                help=argument.description,
                action="store_true",
                default=argument.default,
            )
            return argument_parser

        arg_type = str

        if argument.type == "directory":
            arg_type = Command.Argument.Type.directory
        elif argument.type == "regexp":
            arg_type = Command.Argument.Type.regexp
        elif argument.type == "path":
            arg_type = Path

        default = argument.default

        if not default and argument.is_array:
            default = []

        nargs = "?"
        if argument.is_array:
            nargs = "+"

        argument_parser.add_argument(
            *names,
            type=arg_type,
            default=default,
            nargs=nargs,
            help=argument.description,
        )
        return argument_parser
