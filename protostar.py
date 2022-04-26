import asyncio
import sys
from pathlib import Path

try:
    from src.cli import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade
    from src.protostar_cli import ProtostarCLI

    SCRIPT_ROOT = Path(__file__).parent
    PROTOSTAR_CLI = ProtostarCLI.create(SCRIPT_ROOT)
    PARSER = ArgumentParserFacade(
        PROTOSTAR_CLI,
        default_value_provider=ArgumentDefaultValueFromConfigProvider(
            PROTOSTAR_CLI.project
        ),
    )
    ARGS = PARSER.parse()

    try:
        asyncio.run(PROTOSTAR_CLI.run(ARGS))
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
