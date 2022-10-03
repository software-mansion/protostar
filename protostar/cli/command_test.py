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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("123", 123),
        ("0xf", int("0xf", 16)),
        ("0xDEADC0DE", int("0xDEADC0DE", 16)),
    ],
)
def test_felt_type(test_input, expected):
    result = Command.Argument.Type.felt(test_input)
    assert result == expected


@pytest.mark.parametrize(
    "test_input",
    ["aaaaaaaaa", "0b001", "0o1111", 1 << 512, -1 << 512],
)
def test_felt_type_invalid_input(test_input):
    with pytest.raises(ValueError):
        Command.Argument.Type.felt(test_input)


def test_fee_type():
    assert Command.Argument.Type.fee("auto") == "auto"
    assert Command.Argument.Type.fee("123") == 123
