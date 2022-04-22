import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, Sequence

from src.core.application import Application
from src.core.command import AbstractCommand


class ArgumentParserFacade:
    def __init__(self, argument_parser: ArgumentParser, app: Application) -> None:
        self.argument_parser = argument_parser
        self.command_parsers = self.argument_parser.add_subparsers(dest="command")
        self.app = app

        self._setup_parser()

    def parse(self, input_args: Optional[Sequence[str]] = None) -> Any:
        return self.argument_parser.parse_args(input_args)

    def _add_command(self, command: AbstractCommand) -> "ArgumentParserFacade":
        command_parser = self.command_parsers.add_parser(
            command.name,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        for arg in command.arguments:
            ArgumentParserFacade._add_argument(command_parser, arg)

        return self

    def _add_root_argument(
        self, argument: AbstractCommand.Argument
    ) -> "ArgumentParserFacade":
        ArgumentParserFacade._add_argument(self.argument_parser, argument)
        return self

    @staticmethod
    def _add_argument(
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

    def _setup_parser(self) -> None:
        for cmd in self.app.commands:
            self._add_command(cmd)
