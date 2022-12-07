from pathlib import Path

import pytest

from protostar.formatter.formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)
from protostar.io import LogColorProvider


@pytest.mark.parametrize("check", [True, False])
def test_broken_format_human(check: bool):
    result = BrokenFormattingResult(
        filepath=Path("foo.cairo"),
        checked_only=check,
        exception=Exception("exception"),
    )

    assert (
        result.format_human(LogColorProvider())
        == """\
[BROKEN]      foo.cairo
exception\
"""
    )


@pytest.mark.parametrize(
    "check,expected",
    [
        (True, "[FORMATTED]   foo.cairo"),
        (False, "[UNCHANGED]   foo.cairo"),
    ],
)
def test_correct_format_human(check: bool, expected: str):
    result = CorrectFormattingResult(
        filepath=Path("foo.cairo"),
        checked_only=check,
    )

    assert result.format_human(LogColorProvider()) == expected


@pytest.mark.parametrize(
    "check,expected",
    [
        (True, "[UNFORMATTED] foo.cairo"),
        (False, "[REFORMATTED] foo.cairo"),
    ],
)
def test_incorrect_format_human(check: bool, expected: str):
    result = IncorrectFormattingResult(
        filepath=Path("foo.cairo"),
        checked_only=check,
    )

    assert result.format_human(LogColorProvider()) == expected
