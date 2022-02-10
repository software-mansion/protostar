import os
from logging import INFO, StreamHandler, getLogger

from colorama import init as init_colorama

from src.commands import handle_update_command, remove
from src.commands.install import install
from src.utils import StandardLogFormatter

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
    elif args.command == "update":
        handle_update_command(args)
