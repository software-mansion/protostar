from pathlib import Path
from re import Pattern

import pytest

from .arg_type import map_type_name_to_parser


def test_string_arg_type():
    result = map_type_name_to_parser("str")("123")

    assert isinstance(result, str)


def test_directory_arg_type(tmp_path: Path):
    dir_path = tmp_path / "tmp"
    dir_path.mkdir()

    result = map_type_name_to_parser("directory")(str(dir_path))

    assert isinstance(result, Path)


def test_directory_arg_type_fails_when_no_directory(tmp_path: Path):
    dir_path = tmp_path / "tmp"

    with pytest.raises(AssertionError):
        map_type_name_to_parser("directory")(str(dir_path))


def test_path_arg_type(tmp_path: Path):
    result = map_type_name_to_parser("path")(str(tmp_path))

    assert isinstance(result, Path)


def test_regex_arg_type():
    result = map_type_name_to_parser("regexp")(".*")

    assert isinstance(result, Pattern)
