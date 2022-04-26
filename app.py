# TODO: rename to protostar.py
import asyncio

from src.core import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade
from src.protostar_cli import PROJECT, PROTOSTAR_CLI

parser = ArgumentParserFacade(
    PROTOSTAR_CLI,
    default_value_provider=ArgumentDefaultValueFromConfigProvider(PROJECT),
)
args = parser.parse()


asyncio.run(PROTOSTAR_CLI.run(args))
