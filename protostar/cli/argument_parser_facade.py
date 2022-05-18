from argparse import ArgumentParser, RawTextHelpFormatter, _SubParsersAction
from pathlib import Path
from typing import Any, Optional, Sequence

from protostar.cli.argument_value_from_config_provider import (
    ArgumentValueFromConfigProvider,
)
from protostar.cli.cli_app import CLIApp
from protostar.cli.command import Command


class ArgumentParserFacade:
    def __init__(
        self,
        cli_app: CLIApp,
        default_value_provider: Optional[ArgumentValueFromConfigProvider] = None,
        disable_help=False,
    ) -> None:
        self.argument_parser = ArgumentParser(
            formatter_class=RawTextHelpFormatter, add_help=not disable_help
        )
        self.command_parsers: Optional[_SubParsersAction] = None
        self.cli_app = cli_app
        self._default_value_provider = default_value_provider
        self._setup_parser()

    def parse(
        self, input_args: Optional[Sequence[str]] = None, ignore_unrecognized=False
    ) -> Any:
        if ignore_unrecognized:
            (known_args, _) = self.argument_parser.parse_known_args(input_args)
            return known_args
        return self.argument_parser.parse_args(input_args)

    def print_help(self):
        self.argument_parser.print_help()

    def _setup_parser(self) -> None:
        for cmd in self.cli_app.commands:
            self._add_command(cmd)

        for root_arg in self.cli_app.root_args:
            self._add_root_argument(root_arg)

    def _add_command(self, command: Command) -> "ArgumentParserFacade":
        if not self.command_parsers:
            self.command_parsers = self.argument_parser.add_subparsers(dest="command")

        command_parser = self.command_parsers.add_parser(
            command.name,
            formatter_class=RawTextHelpFormatter,
            description=command.description,
        )
        for arg in command.arguments:
            ArgumentParserFacade._add_argument(
                command_parser,
                self._update_from_config(command, arg),
            )

        return self

    def _add_root_argument(self, argument: Command.Argument) -> "ArgumentParserFacade":
        assert (
            argument.is_positional is False
        ), f"A root argument ({argument.name}) cannot be positional"

        ArgumentParserFacade._add_argument(
            self.argument_parser,
            self._update_from_config(None, argument),
        )
        return self

    def _update_from_config(
        self, command: Optional[Command], argument: Command.Argument
    ) -> Command.Argument:
        if self._default_value_provider:
            new_default = self._default_value_provider.get_default_value(
                command, argument
            )
            if new_default is not None:
                return argument.copy_with(default=new_default)
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
