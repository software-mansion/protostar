# TODO: rename to protostar.py
import asyncio

from src.core import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade
from src.protostar_cli import PROJECT, protostar_cli

parser = ArgumentParserFacade(
    protostar_cli,
    default_value_provider=ArgumentDefaultValueFromConfigProvider(PROJECT),
)
args = parser.parse()


asyncio.run(protostar_cli.run(args))
