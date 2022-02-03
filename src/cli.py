import os
from logging import DEBUG, StreamHandler, getLogger

from colorama import init as init_colorama

from src.commands.install import install

from .utils import StandardLogFormatter

init_colorama()
cwd = os.getcwd()


def cli(args):
    logger = getLogger()
    logger.setLevel(DEBUG)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter())
    logger.addHandler(handler)

    if args.command == "install":
        install(args.package, os.path.join(cwd))
