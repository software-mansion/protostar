from pathlib import Path
from re import Pattern

import pytest

from .arg_type import DirectoryArgType, PathArgType, RegexArgType, StringArgType


def test_string_arg_type():
    arg_type = StringArgType()

    result = arg_type.parse("123")

    assert arg_type.get_name() == "str"
    assert isinstance(result, str)


def test_directory_arg_type(tmp_path: Path):
    dir_path = tmp_path / "tmp"
    dir_path.mkdir()
    arg_type = DirectoryArgType()

    result = arg_type.parse(str(dir_path))

    assert arg_type.get_name() == "directory"
    assert isinstance(result, Path)


def test_directory_arg_type_fails_when_no_directory(tmp_path: Path):
    dir_path = tmp_path / "tmp"
    arg_type = DirectoryArgType()

    with pytest.raises(AssertionError):
        arg_type.parse(str(dir_path))


def test_path_arg_type(tmp_path: Path):
    arg_type = PathArgType()

    result = arg_type.parse(str(tmp_path))

    assert arg_type.get_name() == "path"
    assert isinstance(result, Path)


def test_regex_arg_type():
    arg_type = RegexArgType()

    result = arg_type.parse(".*")

    assert isinstance(result, Pattern)
