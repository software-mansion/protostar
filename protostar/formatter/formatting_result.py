from abc import ABC
from dataclasses import dataclass
from pathlib import Path

from protostar.io import Message, LogColorProvider


@dataclass
class FormattingResult(Message, ABC):
    filepath: Path
    checked_only: bool

    def _format_path(self, fmt: LogColorProvider):
        return fmt.colorize("GRAY", str(self.filepath))


@dataclass
class BrokenFormattingResult(FormattingResult):
    exception: Exception

    def format_human(self, fmt: LogColorProvider) -> str:
        header = _pad_header(_get_broken_header(fmt), self.checked_only, fmt)
        return f"{header} {self._format_path(fmt)}\n{str(self.exception)}"


@dataclass
class CorrectFormattingResult(FormattingResult):
    """
    Indicates that file was already properly formatted when encountered.
    """

    def format_human(self, fmt: LogColorProvider) -> str:
        header = _pad_header(
            _get_correct_header(self.checked_only, fmt), self.checked_only, fmt
        )
        return f"{header} {self._format_path(fmt)}"


@dataclass
class IncorrectFormattingResult(FormattingResult):
    """
    Indicates that file wasn't properly formatted when encountered.
    """

    def format_human(self, fmt: LogColorProvider) -> str:
        header = _pad_header(
            _get_incorrect_header(self.checked_only, fmt), self.checked_only, fmt
        )
        return f"{header} {self._format_path(fmt)}"


def _get_broken_header(fmt: LogColorProvider) -> str:
    return f'[{fmt.colorize("RED", "BROKEN")}]'


def _get_correct_header(check: bool, fmt: LogColorProvider) -> str:
    correct_text = "FORMATTED" if check else "UNCHANGED"
    return f'[{fmt.colorize("CYAN", correct_text)}]'


def _get_incorrect_header(check: bool, fmt: LogColorProvider) -> str:
    incorrect_text = "UNFORMATTED" if check else "REFORMATTED"
    incorrect_color = "YELLOW" if check else "GREEN"
    return f"[{fmt.colorize(incorrect_color, incorrect_text)}]"


def _pad_header(header: str, check: bool, fmt: LogColorProvider) -> str:
    broken_header = _get_broken_header(fmt)
    correct_header = _get_correct_header(check, fmt)
    incorrect_header = _get_incorrect_header(check, fmt)

    padding_size = max(
        len(x) for x in (broken_header, correct_header, incorrect_header)
    )

    return header.ljust(padding_size, " ")
