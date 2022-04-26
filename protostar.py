import asyncio
import sys

try:
    from src.cli import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade
    from src.protostar_cli import PROJECT, PROTOSTAR_CLI

    PARSER = ArgumentParserFacade(
        PROTOSTAR_CLI,
        default_value_provider=ArgumentDefaultValueFromConfigProvider(PROJECT),
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
