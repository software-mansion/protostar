# TODO: rename to protostar.py
import asyncio
from argparse import ArgumentParser

from src.core import ArgumentParserFacade
from src.protostar_cli import protostar_cli

parser = ArgumentParserFacade(ArgumentParser(), protostar_cli)
args = parser.parse()

asyncio.run(protostar_cli.run(args))
