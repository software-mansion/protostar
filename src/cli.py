import os
from src.commands.install import install

cwd = os.getcwd()


def cli(args):
    if args.command == "install":
        install(args.package, os.path.join(cwd))
