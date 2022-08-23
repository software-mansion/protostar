from pathlib import Path

import pytest

from .formatting_summary import FormattingSummary, format_summary
from .formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


@pytest.fixture(name="formatting_summary")
def formatting_summary_fixture() -> FormattingSummary:
    summary = FormattingSummary()

    for i in range(3):
        summary.extend(
            BrokenFormattingResult(Path(str(i)), Exception(f"EXCEPTION({i})"))
        )

    for i in range(3, 5):
        summary.extend(CorrectFormattingResult(Path(str(i))))

    summary.extend(IncorrectFormattingResult(Path("5")))

    return summary


def test_formatting_summary_extending(formatting_summary: FormattingSummary):
    assert len(formatting_summary.broken) == 3
    assert len(formatting_summary.correct) == 2
    assert len(formatting_summary.incorrect) == 1
    assert formatting_summary.get_file_count() == 6


def test_formatting_summary_summary_no_check(formatting_summary: FormattingSummary):
    result = format_summary(formatting_summary, False)
    assert "3 broken" in result
    assert "1 reformatted" in result
    assert "6 total" in result
    assert "unformatted" not in result


def test_formatting_summary_summary_check(formatting_summary: FormattingSummary):
    result = format_summary(formatting_summary, True)
    assert "3 broken" in result
    assert "1 unformatted" in result
    assert "6 total" in result
    assert "reformatted" not in result
