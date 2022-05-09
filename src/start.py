import asyncio
from pathlib import Path

from src.cli.cli_app import CLIApp
from src.protostar_cli import ProtostarCLI
from src.cli import ArgumentValueFromConfigProvider
from src.cli import ArgumentParserFacade


def main(script_root: Path):
    protostar_cli = ProtostarCLI.create(script_root)

    parser = ArgumentParserFacade(
        protostar_cli,
        default_value_provider=ArgumentValueFromConfigProvider(protostar_cli.project),
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
