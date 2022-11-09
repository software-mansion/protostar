from pathlib import Path

from .formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)
from .formatting_summary import FormattingSummary
from ..io import LogColorProvider


def make_formatting_summary(check: bool) -> FormattingSummary:
    summary = FormattingSummary(checked_only=check)

    for i in range(3):
        summary.extend(
            BrokenFormattingResult(
                filepath=Path(str(i)),
                checked_only=check,
                exception=Exception(f"EXCEPTION({i})"),
            )
        )

    for i in range(3, 5):
        summary.extend(
            CorrectFormattingResult(
                filepath=Path(str(i)),
                checked_only=check,
            )
        )

    summary.extend(
        IncorrectFormattingResult(
            filepath=Path("5"),
            checked_only=check,
        )
    )

    return summary


def test_formatting_summary_extending():
    formatting_summary = make_formatting_summary(check=False)
    assert len(formatting_summary.broken) == 3
    assert len(formatting_summary.correct) == 2
    assert len(formatting_summary.incorrect) == 1
    assert len(formatting_summary) == 6


def test_formatting_summary_format_message():
    formatting_summary = make_formatting_summary(check=False)
    assert (
        formatting_summary.format_human(fmt=LogColorProvider())
        == "Summary: 1 reformatted, 3 broken, 6 total."
    )


def test_formatting_summary_format_message_check():
    formatting_summary = make_formatting_summary(check=True)
    assert (
        formatting_summary.format_human(fmt=LogColorProvider())
        == "Summary: 1 unformatted, 3 broken, 6 total."
    )


def test_formatting_summary_format_empty():
    formatting_summary = FormattingSummary()
    assert formatting_summary.format_human(fmt=LogColorProvider()) == "No files found."
