from logging import Logger
from pathlib import Path

from protostar.utils.log_color_provider import LogColorProvider

from .formatting_summary import FormattingSummary
from .formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


def get_colorless_provider() -> LogColorProvider:
    provider = LogColorProvider()
    provider.is_ci_mode = True
    return provider


def get_filled_summary(check: bool) -> FormattingSummary:
    summary = FormattingSummary(Logger(""), check)

    for i in range(3):
        summary.extend(
            BrokenFormattingResult(Path(str(i)), Exception(f"EXCEPTION({i})"))
        )

    for i in range(3, 5):
        summary.extend(CorrectFormattingResult(Path(str(i))))

    summary.extend(IncorrectFormattingResult(Path("5")))

    return summary


def test_formatting_summary_extending():
    summary = get_filled_summary(False)
    assert len(summary.broken) == 3
    assert len(summary.correct) == 2
    assert len(summary.incorrect) == 1
    assert summary.get_file_count() == 6


def test_formatting_summary_summary_no_check():
    log_color_provider = get_colorless_provider()

    summary = get_filled_summary(False)
    result = summary.format_summary(log_color_provider)

    assert "3 broken" in result
    assert "1 reformatted" in result
    assert "6 total" in result
    assert "unformatted" not in result


def test_formatting_summary_summary_check():
    log_color_provider = get_colorless_provider()

    summary = get_filled_summary(True)
    result = summary.format_summary(log_color_provider)

    assert "3 broken" in result
    assert "1 unformatted" in result
    assert "6 total" in result
    assert "reformatted" not in result
