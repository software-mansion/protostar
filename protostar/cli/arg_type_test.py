from pathlib import Path
from re import Pattern

import pytest

from .arg_type import (
    parse_directory_arg_type,
    parse_path,
    parse_regex,
    parse_str_arg_type,
)


def test_string_arg_type():
    result = parse_str_arg_type("123")

    assert isinstance(result, str)


def test_directory_arg_type(tmp_path: Path):
    dir_path = tmp_path / "tmp"
    dir_path.mkdir()

    result = parse_directory_arg_type(str(dir_path))

    assert isinstance(result, Path)


def test_directory_arg_type_fails_when_no_directory(tmp_path: Path):
    dir_path = tmp_path / "tmp"

    with pytest.raises(AssertionError):
        parse_directory_arg_type(str(dir_path))


def test_path_arg_type(tmp_path: Path):
    result = parse_path(str(tmp_path))

    assert isinstance(result, Path)


def test_regex_arg_type():
    result = parse_regex(".*")

    assert isinstance(result, Pattern)
