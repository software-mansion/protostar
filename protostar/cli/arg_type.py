import re
from pathlib import Path
from re import Pattern
from typing import Any, Callable, Literal

ArgTypeName = Literal[
    "str",
    "directory",
    "path",
    "bool",
    "regexp",
    "int",
]


def map_type_name_to_parser(argument_type: str) -> Callable[[str], Any]:
    type_name_to_parser_mapping: dict[ArgTypeName, Callable[[str], Any]] = {
        "str": str,
        "bool": bool,
        "int": int,
        "directory": parse_directory_arg_type,
        "regexp": re.compile,
        "path": Path,
    }
    if argument_type in type_name_to_parser_mapping:
        return type_name_to_parser_mapping[argument_type]
    assert False, "Unknown argument type"


def parse_directory_arg_type(arg: str) -> Path:
    path = Path(arg)
    assert path.is_dir(), f'"{str(path)}" is not a valid directory path'
    return path


def parse_regex(arg: str) -> Pattern:
    return re.compile(arg)
