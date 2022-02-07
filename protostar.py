from argparse import ArgumentParser
from pathlib import Path

from src import cli

root_parser = ArgumentParser()
root_subparsers = root_parser.add_subparsers(dest="command")

cmd_install_parser = root_subparsers.add_parser("install")
cmd_install_parser.add_argument("package", type=str)

cmd_remove_parser = root_subparsers.add_parser("remove")
cmd_remove_parser.add_argument("package", type=str)

cmd_new_parser = root_subparsers.add_parser("new")
cmd_new_parser.add_argument("project_name", type=str)

cli(root_parser.parse_args(), Path(__file__).parent)
