import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, Sequence

from src.cli.argument_default_value_from_config_provider import (
    ArgumentDefaultValueFromConfigProvider,
)
from src.cli.cli_app import CLIApp
from src.cli.command import Command


class ArgumentParserFacade:
    def __init__(
        self,
        cli_app: CLIApp,
        default_value_provider: Optional[ArgumentDefaultValueFromConfigProvider] = None,
    ) -> None:
        self.argument_parser = ArgumentParser()
        self.command_parsers = self.argument_parser.add_subparsers(dest="command")
        self.cli_app = cli_app
        self._default_value_provider = default_value_provider

        self._setup_parser()

    def parse(self, input_args: Optional[Sequence[str]] = None) -> Any:
        return self.argument_parser.parse_args(input_args)

    def print_help(self):
        self.argument_parser.print_help()

    def _setup_parser(self) -> None:
        for cmd in self.cli_app.commands:
            self._add_command(cmd)

        for root_arg in self.cli_app.root_args:
            self._add_root_argument(root_arg)

    def _add_command(self, command: Command) -> "ArgumentParserFacade":
        command_parser = self.command_parsers.add_parser(
            command.name,
            formatter_class=argparse.RawTextHelpFormatter,
            description=command.description,
        )
        for arg in command.arguments:
            self._update_arg_default_value_if_necessary(command, arg)
            ArgumentParserFacade._add_argument(command_parser, arg)

        return self

    def _add_root_argument(self, argument: Command.Argument) -> "ArgumentParserFacade":
        assert (
            argument.is_positional is False
        ), f"A root argument ({argument.name}) cannot be positional"

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
        name = argument.name if argument.is_positional else f"--{argument.name}"
        short_name = f"-{argument.short_name}" if argument.short_name else None

        names = [name]
        if short_name:
            names.append(short_name)

        if argument.type == "bool":
            assert (
                argument.is_positional is False
            ), "A boolean can't be positional argument"
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

        kwargs = {}
        if argument.is_required and not argument.is_positional:
            kwargs["required"] = True

        if argument.is_positional and not argument.is_required:
            kwargs["nargs"] = "?"

        if argument.is_array:
            kwargs["nargs"] = "+"

        argument_parser.add_argument(
            *names,
            type=arg_type,
            default=default,
            help=argument.description,
            **kwargs,
        )
        return argument_parser
