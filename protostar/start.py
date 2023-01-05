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
from protostar.argument_parser.abi_obtainer import abi_from_args


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


def run_protostar(
    protostar_cli: ProtostarCLI,
    parser: ArgumentParserFacade,
    args: Any,
):
    try:
        if hasattr(args, "inputs") and isinstance(args.inputs, dict):
            abi = asyncio.run(abi_from_args(args))
            target_abi_item = None
            for abi_item in abi:
                if abi_item["name"] == args.function:
                    target_abi_item = abi_item
                    break
            assert target_abi_item
            inputs_as_list = []
            for input_item in target_abi_item["inputs"]:
                new_item = args.inputs[input_item["name"]]
                if isinstance(new_item, list):
                    inputs_as_list += new_item
                else:
                    inputs_as_list.append(new_item)
            args.inputs = inputs_as_list
        asyncio.run(protostar_cli.run(args))
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        raise err
