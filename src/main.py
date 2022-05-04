# pylint: disable=import-outside-toplevel
import asyncio
from pathlib import Path

from src.cli.cli_app import CLIApp
from src.protostar_cli import ProtostarCLI


def main(script_root: Path):
    # mocker.patch doesn't work when imported normally
    from src.cli import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade

    protostar_cli = ProtostarCLI.create(script_root)
    parser = ArgumentParserFacade(
        protostar_cli,
        default_value_provider=ArgumentDefaultValueFromConfigProvider(
            protostar_cli.project
        ),
    )
    args = parser.parse()

    try:
        asyncio.run(protostar_cli.run(args))
    except CLIApp.CommandNotFoundError:
        parser.print_help()
    except Exception as err:
        print(
            "Unexpected Protostar error. Report it here:\nhttps://github.com/software-mansion/protostar/issues\n"
        )
        raise err
