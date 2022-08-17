from dataclasses import dataclass
from pathlib import Path


@dataclass
class FormattingResult:
    filepath: Path


@dataclass
class BrokenFormattingResult(FormattingResult):
    exception: Exception


@dataclass
class CorrectFormattingResult(FormattingResult):
    """
    Indicates that file was already properly formatted when encountered
    """


@dataclass
class IncorrectFormattingResult(FormattingResult):
    """
    Indicates that file wasn't properly formatted when encountered
    """
