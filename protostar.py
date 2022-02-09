import asyncio
import re
from argparse import ArgumentParser
from pathlib import Path
from re import Pattern
from src import cli

SCRIPT_ROOT = Path(__file__).parent


def regexp(input_string: str) -> Pattern:
    return re.compile(input_string)


def directory(directory_path: str) -> Path:
    pth = Path(directory_path)
    assert pth.is_dir(), "Given argument is not a valid directory path"
    return pth


root_parser = ArgumentParser()
root_subparsers = root_parser.add_subparsers(dest="command")

cmd_install_parser = root_subparsers.add_parser("install")
cmd_install_parser.add_argument("package", type=str)

cmd_remove_parser = root_subparsers.add_parser("remove")
cmd_remove_parser.add_argument("package", type=str)


cmd_new_parser = root_subparsers.add_parser("new")
cmd_new_parser.add_argument("project_name", type=str)

cli(root_parser.parse_args(), SCRIPT_ROOT)

cmd_test_parser = root_subparsers.add_parser("test")
cmd_test_parser.add_argument("sources-root", type=directory)
cmd_test_parser.add_argument(
    "--omit",
    "-o",
    type=regexp,
    required=False,
    help="A path regexp, which omits the test file if it matches the pattern",
)
cmd_test_parser.add_argument(
    "--match",
    "-m",
    type=regexp,
    required=False,
    help="A path regexp, which omits the test file if it does not match the pattern",
)
cmd_test_parser.add_argument(
    "--cairo-path",
    "-cp",
    nargs="+",
    default=[],
    type=directory,
    help="Paths which will be searched in test contracts compilation",
    required=False,
)
cmd_test_parser.add_argument(
    "--cairo-path-recursive",
    "-cpr",
    nargs="+",
    default=[],
    type=directory,
    help="Paths which will be searched recursively in test contracts compilation",
    required=False,
)

asyncio.run(cli(root_parser.parse_args(), SCRIPT_ROOT))
