import os
from logging import INFO, StreamHandler, getLogger

from colorama import init as init_colorama

from .commands import install, remove
from .utils import StandardLogFormatter

init_colorama()
cwd = os.getcwd()


def cli(args):
    logger = getLogger()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter())
    logger.addHandler(handler)

    if args.command == "install":
        install(args.package, cwd)
    elif args.command == "remove":
        remove(args.package, cwd)
