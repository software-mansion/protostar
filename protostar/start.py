import asyncio
import sys
from pathlib import Path
from typing import Any

from protostar.cli import (
    ArgumentParserFacade,
    ArgumentValueFromConfigProvider,
    CLIApp,
    MissingRequiredArgumentException,
)
from protostar.composition_root import build_di_container
from protostar.configuration_profile_cli import ConfigurationProfileCLI
from protostar.protostar_cli import ProtostarCLI
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader


def main(script_root: Path, start_time: float = 0):
    container = build_di_container(script_root, start_time)
    arg_parser = build_parser(container.protostar_cli, container.protostar_toml_reader)
    args = parse_args(arg_parser)
    run_protostar(container.protostar_cli, args, arg_parser)


def build_parser(
    protostar_cli: ProtostarCLI, protostar_toml_reader: ProtostarTOMLReader
) -> ArgumentParserFacade:
    configuration_profile_name = (
        ArgumentParserFacade(ConfigurationProfileCLI(), disable_help=True)
        .parse(ignore_unrecognized=True)
        .profile
    )
    argument_value_from_config_provider = ArgumentValueFromConfigProvider(
        protostar_toml_reader,
        configuration_profile_name,
    )
    return ArgumentParserFacade(protostar_cli, argument_value_from_config_provider)


def parse_args(parser: ArgumentParserFacade) -> Any:
    try:
        return parser.parse()
    except MissingRequiredArgumentException as err:
        print(err.message)
        sys.exit(1)


def run_protostar(protostar_cli: ProtostarCLI, args: Any, parser: ArgumentParserFacade):
    try:
        asyncio.run(protostar_cli.run(args))
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        raise err
