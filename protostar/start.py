import asyncio
from pathlib import Path

from protostar.cli import (
    ArgumentParserFacade,
    ArgumentValueFromConfigProvider,
    CLIApp,
    MissingRequiredArgumentException,
)
from protostar.composition_root import build_di_container
from protostar.configuration_profile_cli import ConfigurationProfileCLI
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG


def main(script_root: Path):
    di_container = build_di_container(script_root)
    protostar_cli = di_container.protostar_cli
    protostar_toml_reader = di_container.protostar_toml_reader

    configuration_profile_name = (
        ArgumentParserFacade(ConfigurationProfileCLI(), disable_help=True)
        .parse(ignore_unrecognized=True)
        .profile
    )
    argument_value_from_config_provider = ArgumentValueFromConfigProvider(
        protostar_toml_reader,
        configuration_profile_name,
    )
    parser = ArgumentParserFacade(protostar_cli, argument_value_from_config_provider)

    try:
        asyncio.run(protostar_cli.run(parser.parse()))
    except MissingRequiredArgumentException as err:
        print(err.message)
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        raise err
