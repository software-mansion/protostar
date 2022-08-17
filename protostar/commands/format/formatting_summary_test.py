from logging import Logger
from pathlib import Path

from protostar.utils.log_color_provider import LogColorProvider

from .formatting_summary import FormatingSummary
from .formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


def get_colorless_provider() -> LogColorProvider:
    provider = LogColorProvider()
    provider.is_ci_mode = True
    return provider


def get_filled_summary(check: bool) -> FormatingSummary:
    summary = FormatingSummary(Logger(""), check)

    for i in range(3):
        summary.extend(
            BrokenFormattingResult(Path(str(i)), Exception(f"EXCEPTION({i})"))
        )

    for i in range(3, 5):
        summary.extend(CorrectFormattingResult(Path(str(i))))

    summary.extend(IncorrectFormattingResult(Path("5")))

    return summary


def is_range_in_result(input_range: range, result: str):
    return all(str(x) in result for x in input_range)


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
    assert "incorrectly formatted" not in result


def test_formatting_summary_summary_check():
    log_color_provider = get_colorless_provider()

    summary = get_filled_summary(True)
    result = summary.format_summary(log_color_provider)

    assert "3 broken" in result
    assert "1 incorrectly formatted" in result
    assert "6 total" in result
    assert "reformatted" not in result


def test_formatting_summary_files_no_check():
    log_color_provider = get_colorless_provider()

    summary = get_filled_summary(False)
    result = summary.format_files(log_color_provider)

    assert "BROKEN" in result
    assert "UNCHANGED" in result
    assert "REFORMATTED" in result
    assert "CORRECTLY FORMATTED" not in result
    assert "INCORRECTLY FORMATTED" not in result
    assert is_range_in_result(range(5), result)


def test_formatting_summary_files_check():
    log_color_provider = get_colorless_provider()

    summary = get_filled_summary(True)
    result = summary.format_files(log_color_provider)

    assert "BROKEN" in result
    assert "UNCHANGED" not in result
    assert "REFORMATTED" not in result
    assert "CORRECTLY FORMATTED" in result
    assert "INCORRECTLY FORMATTED" in result
    assert is_range_in_result(range(5), result)


def test_formatting_summary_files_exceptions():
    log_color_provider = get_colorless_provider()

    summary = get_filled_summary(False)
    result = summary.format_files(log_color_provider)

    assert "EXCEPTION(0)" in result
    assert "EXCEPTION(1)" in result
    assert "EXCEPTION(2)" in result
