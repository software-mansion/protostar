from argparse import ArgumentParser, Namespace, RawTextHelpFormatter, _SubParsersAction
from typing import (
    Any,
    Callable,
    Generic,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
)

from .arg_type import ArgTypeName, map_type_name_to_parser
from .argument import Argument
from .cli_app import CLIApp
from .command import Command
from .config_file_argument_resolver import ConfigFileArgumentResolverProtocol

ArgTypeNameT_contra = TypeVar(
    "ArgTypeNameT_contra", bound=ArgTypeName, contravariant=True
)


class ParserResolverProtocol(Protocol, Generic[ArgTypeNameT_contra]):
    def __call__(self, argument_type: ArgTypeNameT_contra) -> Callable[[str], Any]:
        ...


class ArgumentParserFacade(Generic[ArgTypeNameT_contra]):
    def __init__(
        self,
        cli_app: CLIApp[ArgTypeNameT_contra],
        config_file_argument_value_resolver: Optional[
            ConfigFileArgumentResolverProtocol
        ] = None,
        parser_resolver: ParserResolverProtocol[
            ArgTypeNameT_contra
        ] = map_type_name_to_parser,
        disable_help=False,
    ) -> None:
        self.argument_parser = ArgumentParser(
            formatter_class=RawTextHelpFormatter, add_help=not disable_help
        )
        self.command_parsers: Optional[_SubParsersAction] = None
        self.cli_app = cli_app
        self._config_file_argument_value_resolver = config_file_argument_value_resolver
        self._parser_resolver = parser_resolver
        self._setup_parser()

    def parse(
        self, input_args: Optional[Sequence[str]] = None, ignore_unrecognized=False
    ) -> Any:
        args: Namespace
        if ignore_unrecognized:
            (known_args, _) = self.argument_parser.parse_known_args(input_args)
            args = known_args
        else:
            args = self.argument_parser.parse_args(input_args)

        missing_data = self._find_missing_required_arg_in_project(args)
        if missing_data:
            (command, arg) = missing_data
            raise MissingRequiredArgumentException(
                argument_name=arg.name, command_name=command.name if command else None
            )

        return args

    def print_help(self):
        self.argument_parser.print_help()

    def _find_missing_required_arg_in_project(
        self, parsed_args: Namespace
    ) -> Optional[Tuple[Optional[Command], Argument]]:
        missing_arg = self._find_missing_required_arg(
            self.cli_app.root_args, parsed_args
        )
        if missing_arg:
            return (None, missing_arg)

        if hasattr(parsed_args, "command") and parsed_args.command:
            command = self.cli_app.get_command_by_name(parsed_args.command)
            missing_arg = self._find_missing_required_arg(
                command.arguments, parsed_args
            )
            if missing_arg:
                return (command, missing_arg)
        return None

    @staticmethod
    def _find_missing_required_arg(
        declared_args: List[Argument[ArgTypeNameT_contra]], parsed_args: Namespace
    ) -> Optional[Argument[ArgTypeNameT_contra]]:
        for arg in declared_args:
            if not arg.is_required:
                continue

            arg_name = arg.name.replace("-", "_")
            is_argument_set = hasattr(parsed_args, arg_name) and getattr(
                parsed_args, arg_name
            )
            if not is_argument_set:
                return arg
        return None

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
            self._add_argument(
                command_parser,
                self._update_from_config(command, arg),  # type: ignore
            )

        return self

    def _add_root_argument(
        self, argument: Argument[ArgTypeNameT_contra]
    ) -> "ArgumentParserFacade":
        assert (
            argument.is_positional is False
        ), f"A root argument ({argument.name}) cannot be positional"

        self._add_argument(
            self.argument_parser,
            self._update_from_config(None, argument),
        )
        return self

    def _update_from_config(
        self, command: Optional[Command], argument: Argument[ArgTypeNameT_contra]
    ) -> Argument[ArgTypeNameT_contra]:
        if self._config_file_argument_value_resolver:
            new_default = self._config_file_argument_value_resolver.resolve_argument(
                command.name if command else None, argument.name
            )
            if new_default is not None:
                return argument.copy_with(default=new_default)
        return argument

    def _add_argument(
        self, argument_parser: ArgumentParser, argument: Argument[ArgTypeNameT_contra]
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

        arg_type = self._parser_resolver(argument.type)

        default = argument.default

        if not default and argument.is_array:
            default = []

        kwargs = {}

        if argument.is_positional:
            kwargs["nargs"] = "?"

        if argument.is_array:
            kwargs["nargs"] = "*"

        argument_parser.add_argument(
            *names,
            type=arg_type,
            default=default,
            help=argument.description,
            **kwargs,
        )
        return argument_parser


class MissingRequiredArgumentException(Exception):
    def __init__(self, argument_name: str, command_name: Optional[str]) -> None:
        self.message = (
            f"Command `{command_name}` expects argument: `{argument_name}`"
            if command_name
            else f"Missing required argument: `{argument_name}`"
        )
        super().__init__(self.message)
