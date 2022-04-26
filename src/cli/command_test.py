from pathlib import Path
from typing import Pattern

import pytest

from src.cli.command import Command


def test_regexp_type():
    result = Command.Argument.Type.regexp(".*")
    assert isinstance(result, Pattern)


def test_directory_type(tmpdir):
    result = Command.Argument.Type.directory(tmpdir)
    assert isinstance(result, Path)


def test_directory_type_checks_existence():
    with pytest.raises(AssertionError):
        Command.Argument.Type.directory("!@#$")
