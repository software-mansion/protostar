# pylint: disable=import-outside-toplevel
import asyncio
import sys
from pathlib import Path


def main(script_root: Path):
    try:
        from src.cli import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade
        from src.protostar_cli import ProtostarCLI

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
        except Exception as err:
            print(
                "Unexpected Protostar error. Report it here:\nhttps://github.com/software-mansion/protostar/issues\n"
            )
            raise err

    except ImportError as err:
        # pylint: disable=no-member
        if err.msg.startswith("Failed to initialize: Bad git executable."):
            print(
                "Protostar requires git executable to be specified in $PATH. Did you install git?"
            )
            sys.exit()
        raise err
