from argparse import ArgumentParser

from src import cli

root_parser = ArgumentParser()
root_subparsers = root_parser.add_subparsers(dest="command")

cmd_install_parser = root_subparsers.add_parser("install")
cmd_install_parser.add_argument("package", type=str)

cmd_remove_parser = root_subparsers.add_parser("remove")
cmd_remove_parser.add_argument("package", type=str)

cli(root_parser.parse_args())
