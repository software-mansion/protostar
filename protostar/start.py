import asyncio
from pathlib import Path

from protostar.cli import ArgumentParserFacade, ArgumentValueFromConfigProvider
from protostar.cli.cli_app import CLIApp
from protostar.protostar_cli import ConfigurationProfileCLISchema, ProtostarCLI
from protostar.protostar_exception import UNEXPECTED_PROTOSTAR_ERROR_MSG


def main(script_root: Path):
    protostar_cli = ProtostarCLI.create(script_root)

    configuration_profile_name = (
        ArgumentParserFacade(ConfigurationProfileCLISchema(), disable_help=True)
        .parse(ignore_unrecognized=True)
        .profile
    )

    parser = ArgumentParserFacade(
        protostar_cli,
        default_value_provider=ArgumentValueFromConfigProvider(
            protostar_cli.protostar_toml_reader,
            configuration_profile_name=configuration_profile_name,
        ),
    )

    try:
        asyncio.run(protostar_cli.run(parser.parse()))
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(UNEXPECTED_PROTOSTAR_ERROR_MSG)
        raise err
