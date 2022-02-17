import argparse
import asyncio
import re
from argparse import ArgumentParser
from pathlib import Path
from re import Pattern

from src import cli

SCRIPT_ROOT = Path(__file__).parent

PACKAGE_CORE_FORMATS_HELP_MESSAGE = """a package reference in one of the following formats:
- GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]
    e.g. software-mansion/starknet.py@0.1.5-alpha
- URL_TO_THE_REPOSITORY
    e.g. https://github.com/software-mansion/starknet.py
- SSH_URI
    e.g. git@github.com:software-mansion/starknet.py.git
"""


INSTALLED_PACKAGE_FORMATS_HELP_MESSAGE = (
    PACKAGE_CORE_FORMATS_HELP_MESSAGE
    + '- PACKAGE_DIRECTORY_NAME e.g. "starknet_py", if the package location is "lib/starknet_py"'
)


def regexp(input_string: str) -> Pattern:
    return re.compile(input_string)


def directory(directory_path: str) -> Path:
    pth = Path(directory_path)
    assert pth.is_dir(), f'"{str(pth)}" is not a valid directory path'
    return pth


def cairo_file(file_path: str) -> Path:
    pth = Path(file_path)
    assert pth.is_file(), f'"{str(pth)}" is not a valid directory path'
    assert (
        pth.suffix == ".cairo"
    ), f"The input file must be a cairo file, provided {pth.suffix} suffix"
    return pth


root_parser = ArgumentParser()
root_parser.add_argument(
    "--no-color", default=False, help="disable colors", action="store_true"
)

root_subparsers = root_parser.add_subparsers(dest="command")

cmd_install_parser = root_subparsers.add_parser(
    "install",
    formatter_class=argparse.RawTextHelpFormatter,
)
cmd_install_parser.add_argument(
    "package",
    type=str,
    nargs="?",
    default="",
    help=PACKAGE_CORE_FORMATS_HELP_MESSAGE,
)
cmd_install_parser.add_argument(
    "--name",
    type=str,
    help="custom package name — useful in resolving package name conflicts",
)

cmd_remove_parser = root_subparsers.add_parser(
    "remove", formatter_class=argparse.RawTextHelpFormatter
)
cmd_remove_parser.add_argument(
    "package",
    type=str,
    help=INSTALLED_PACKAGE_FORMATS_HELP_MESSAGE,
)


cmd_init_parser = root_subparsers.add_parser("init")


cmd_update_parser = root_subparsers.add_parser(
    "update",
    formatter_class=argparse.RawTextHelpFormatter,
)
cmd_update_parser.add_argument(
    "package",
    type=str,
    default="",
    nargs="?",
    help=INSTALLED_PACKAGE_FORMATS_HELP_MESSAGE,
)


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
    nargs="+",
    default=[],
    type=directory,
    help="Paths which will be searched in test contracts compilation",
    required=False,
)
cmd_test_parser.add_argument(
    "--cairo-path-recursive",
    nargs="+",
    default=[],
    type=directory,
    help="Paths which will be searched recursively in test contracts compilation",
    required=False,
)

cmd_compile_parser = root_subparsers.add_parser("compile")
cmd_compile_parser.add_argument(
    "input-files", type=cairo_file, nargs="+", help="Input files"
)
cmd_compile_parser.add_argument(
    "--output",
    type=argparse.FileType("w", encoding="utf-8"),
    help="Contract output file",
    required=False,
)
cmd_compile_parser.add_argument(
    "--abi",
    type=argparse.FileType("w", encoding="utf-8"),
    help="Contract's ABI output file",
    required=False,
)
cmd_compile_parser.add_argument(
    "--libraries-root",
    type=directory,
    help="""
        Directory where the libraries are installed 
        (assumed it's installed with protostar, otherwise see --cairo-path)
    """,
    default=Path(Path.cwd(), "lib"),
)
cmd_compile_parser.add_argument(
    "--cairo-path",
    type=directory,
    nargs="+",
    help="Additional directories to look for sources",
    default=[],
    required=False,
)


try:
    asyncio.run(cli(root_parser.parse_args(), SCRIPT_ROOT))
except Exception as err:
    print(
        "Unexpected Protostar error. Report it here:\nhttps://github.com/software-mansion/protostar/issues\n"
    )
    raise err
