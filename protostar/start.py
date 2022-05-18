import asyncio
from pathlib import Path

from protostar.cli import ArgumentParserFacade, ArgumentValueFromConfigProvider
from protostar.cli.cli_app import CLIApp
from protostar.protostar_cli import ConfigurationProfileCLI, ProtostarCLI


def main(script_root: Path):
    protostar_cli = ProtostarCLI.create(script_root)

    parser = ArgumentParserFacade(
        protostar_cli,
        default_value_provider=ArgumentValueFromConfigProvider(
            protostar_cli.project,
            configuration_profile_name=ArgumentParserFacade(
                ConfigurationProfileCLI(), disable_help=True
            )
            .parse(ignore_unrecognized=True)
            .profile,
        ),
    )

    try:
        asyncio.run(protostar_cli.run(parser.parse()))
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(
            "Unexpected Protostar error. Report it here:\nhttps://github.com/software-mansion/protostar/issues\n"
        )
        raise err
