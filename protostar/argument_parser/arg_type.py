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
    "float",
]


def map_type_name_to_parser(argument_type: ArgTypeName) -> Callable[[str], Any]:
    type_name_to_parser_mapping: dict[ArgTypeName, Callable[[str], Any]] = {
        "str": str,
        "bool": parse_bool_arg_type,
        "int": int,
        "float": float,
        "directory": parse_directory_arg_type,
        "regexp": re.compile,
        "path": Path,
    }
    if argument_type in type_name_to_parser_mapping:
        return type_name_to_parser_mapping[argument_type]
    assert False, f"Unknown argument type {argument_type}"


def parse_bool_arg_type(arg: str) -> bool:
    if arg in ["false", "False", "0"]:
        return False
    return bool(arg)


def parse_directory_arg_type(arg: str) -> Path:
    path = Path(arg)
    assert path.is_dir(), f'"{str(path)}" is not a valid directory path'
    return path


def parse_regex(arg: str) -> Pattern:
    return re.compile(arg)
