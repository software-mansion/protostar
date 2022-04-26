# TODO: rename to protostar.py
import asyncio
from argparse import ArgumentParser

from src.core import ArgumentDefaultValueFromConfigProvider, ArgumentParserFacade
from src.protostar_cli import PROJECT, protostar_cli

parser = ArgumentParserFacade(
    ArgumentParser(),
    protostar_cli,
    default_value_provider=ArgumentDefaultValueFromConfigProvider(PROJECT),
)
args = parser.parse()


asyncio.run(protostar_cli.run(args))
