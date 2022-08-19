from pathlib import Path

from .formatting_summary import FormattingSummary, format_summary
from .formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


def get_filled_summary() -> FormattingSummary:
    summary = FormattingSummary()

    for i in range(3):
        summary.extend(
            BrokenFormattingResult(Path(str(i)), Exception(f"EXCEPTION({i})"))
        )

    for i in range(3, 5):
        summary.extend(CorrectFormattingResult(Path(str(i))))

    summary.extend(IncorrectFormattingResult(Path("5")))

    return summary


def test_formatting_summary_extending():
    summary = get_filled_summary()
    assert len(summary.broken) == 3
    assert len(summary.correct) == 2
    assert len(summary.incorrect) == 1
    assert summary.get_file_count() == 6


def test_formatting_summary_summary_no_check():
    summary = get_filled_summary()
    result = format_summary(summary, False)

    assert "3 broken" in result
    assert "1 reformatted" in result
    assert "6 total" in result
    assert "unformatted" not in result


def test_formatting_summary_summary_check():
    summary = get_filled_summary()
    result = format_summary(summary, True)

    assert "3 broken" in result
    assert "1 unformatted" in result
    assert "6 total" in result
    assert "reformatted" not in result
