from pathlib import Path
from typing import Pattern

import pytest

from protostar.cli.command import Command


def test_regexp_type():
    result = Command.Argument.Type.regexp(".*")
    assert isinstance(result, Pattern)


def test_directory_type(tmpdir):
    result = Command.Argument.Type.directory(tmpdir)
    assert isinstance(result, Path)


def test_directory_type_checks_existence():
    with pytest.raises(AssertionError):
        Command.Argument.Type.directory("!@#$")


def test_int_type():
    ints = ["123", "0xf", "0b001", "0o444", "0xDEADC0DE"]
    for i in ints:
        result = Command.Argument.Type.int(i)
        assert isinstance(result, int)
