import os

from .commands import install, remove

cwd = os.getcwd()


def cli(args):
    if args.command == "install":
        install(args.package, cwd)
    elif args.command == "remove":
        remove(args.package, cwd)
