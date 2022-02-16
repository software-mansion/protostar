import argparse
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
root_subparsers = root_parser.add_subparsers(dest="command")

cmd_install_parser = root_subparsers.add_parser("install")
cmd_install_parser.add_argument("package", type=str, nargs="?", default="")
cmd_install_parser.add_argument(
    "--name", type=str, help="Custom package's directory name"
)

cmd_remove_parser = root_subparsers.add_parser("remove")
cmd_remove_parser.add_argument("package", type=str)


cmd_init_parser = root_subparsers.add_parser("init")


cmd_update_parser = root_subparsers.add_parser("update")
cmd_update_parser.add_argument("package", type=str, default="", nargs="?")


cmd_test_parser = root_subparsers.add_parser("test")
cmd_test_parser.add_argument("tests-root", type=directory)
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

cmd_compile_parser = root_subparsers.add_parser("build")
cmd_compile_parser.add_argument(
    "--output",
    type=Path,
    required=False,
    default=Path("build"),
    help="Output directory, which will be used to put the compiled contracts in",
)

cmd_compile_parser.add_argument(
    "--cairo-path",
    type=directory,
    nargs="+",
    help="Additional directories to look for sources",
    default=[],
    required=False,
)


asyncio.run(cli(root_parser.parse_args(), SCRIPT_ROOT))
