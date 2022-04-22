# TODO: rename to protostar.py
import asyncio
from argparse import ArgumentParser

from src.core import ArgumentParserFacade
from src.protostar_app import protostar_app

parser = ArgumentParserFacade(ArgumentParser(), protostar_app)
args = parser.parse()

asyncio.run(protostar_app.run(args))
