import asyncio
import sys
from pathlib import Path
from typing import Any, Optional

from protostar.argument_parser import (
    ArgumentParserFacade,
    CLIApp,
    MissingRequiredArgumentException,
)
from protostar.composition_root import build_di_container
from protostar.configuration_profile_cli import ConfigurationProfileCLI
from protostar.protostar_cli import ProtostarCLI
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG


def main(script_root: Path, start_time: float = 0):
    profile_name = get_active_configuration_profile_name()
    container = build_di_container(script_root, profile_name, start_time)
    args = parse_args(container.argument_parser_facade)
    run_protostar(container.protostar_cli, container.argument_parser_facade, args)


def get_active_configuration_profile_name() -> Optional[str]:
    return (
        ArgumentParserFacade(ConfigurationProfileCLI(), disable_help=True)
        .parse(ignore_unrecognized=True)
        .profile
    )


def parse_args(parser: ArgumentParserFacade) -> Any:
    try:
        return parser.post_parse(parser.parse())
    except MissingRequiredArgumentException as err:
        print(err.message)
        sys.exit(1)


def run_protostar(protostar_cli: ProtostarCLI, parser: ArgumentParserFacade, args: Any):
    try:
        asyncio.run(protostar_cli.run(args))
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        raise err
