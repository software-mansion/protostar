from typing import List
from dataclasses import dataclass
from pathlib import Path

from protostar.io.log_color_provider import log_color_provider


@dataclass
class FormattingResult:
    filepath: Path


@dataclass
class BrokenFormattingResult(FormattingResult):
    exception: Exception


@dataclass
class CorrectFormattingResult(FormattingResult):
    """
    Indicates that file was already properly formatted when encountered.
    """


@dataclass
class IncorrectFormattingResult(FormattingResult):
    """
    Indicates that file wasn't properly formatted when encountered.
    """


def format_formatting_result(formatting_result: FormattingResult, check: bool) -> str:
    result: List[str] = []

    broken_header = _get_broken_header()
    correct_header = _get_correct_header(check)
    incorrect_header = _get_incorrect_header(check)

    padding = max(len(x) for x in (broken_header, correct_header, incorrect_header)) + 2

    broken_header = _pad_header(broken_header, padding)
    incorrect_header = _pad_header(incorrect_header, padding)
    correct_header = _pad_header(correct_header, padding)

    if isinstance(formatting_result, BrokenFormattingResult):
        result.append(broken_header)
        result.append(_get_formatted_path(formatting_result))
        result.append("\n")
        result.append(str(formatting_result.exception))

    elif isinstance(formatting_result, CorrectFormattingResult):
        result.append(correct_header)
        result.append(_get_formatted_path(formatting_result))

    elif isinstance(formatting_result, IncorrectFormattingResult):
        result.append(incorrect_header)
        result.append(_get_formatted_path(formatting_result))

    return "".join(result)


def _get_formatted_path(formatting_result: FormattingResult) -> str:
    return log_color_provider.colorize("GRAY", str(formatting_result.filepath))


def _get_broken_header() -> str:
    return f'[{log_color_provider.colorize("RED", "BROKEN")}]'


def _get_correct_header(check: bool) -> str:
    correct_text = "FORMATTED" if check else "UNCHANGED"
    return f'[{log_color_provider.colorize("CYAN", correct_text)}]'


def _get_incorrect_header(check: bool) -> str:
    incorrect_text = "UNFORMATTED" if check else "REFORMATTED"
    incorrect_color = "YELLOW" if check else "GREEN"
    return f"[{log_color_provider.colorize(incorrect_color, incorrect_text)}]"


def _pad_header(header: str, padding_size: int) -> str:
    return header.ljust(padding_size, " ")
