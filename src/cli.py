import os
from src.commands.install import install

cwd = os.getcwd()


def cli(args):
    if args.command == "install":
        result = install(args.package, os.path.join(cwd))
        print(result)
