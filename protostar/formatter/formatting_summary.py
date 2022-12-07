from dataclasses import dataclass, field
from typing import List

from protostar.formatter.formatting_result import (
    FormattingResult,
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)
from protostar.io import LogColorProvider, Message


@dataclass
class FormattingSummary(Message):
    checked_only: bool = False

    broken: List[BrokenFormattingResult] = field(default_factory=list)
    incorrect: List[IncorrectFormattingResult] = field(default_factory=list)
    correct: List[CorrectFormattingResult] = field(default_factory=list)

    def extend(self, formatting_result: FormattingResult):
        if isinstance(formatting_result, BrokenFormattingResult):
            self.broken.append(formatting_result)
        elif isinstance(formatting_result, CorrectFormattingResult):
            self.correct.append(formatting_result)
        elif isinstance(formatting_result, IncorrectFormattingResult):
            self.incorrect.append(formatting_result)

    def __len__(self) -> int:
        return len(self.broken) + len(self.correct) + len(self.incorrect)

    def any_unformatted_or_broken(self, check: bool):
        return bool(len(self.broken) + (len(self.incorrect) if check else 0))

    def format_human(self, fmt: LogColorProvider) -> str:
        total = len(self)
        if total == 0:
            return "No files found."

        broken = len(self.broken)
        incorrect = len(self.incorrect)

        result: List[str] = [fmt.bold("Summary: ")]

        text = "unformatted" if self.checked_only else "reformatted"
        color = "YELLOW" if self.checked_only else "GREEN"

        result.append(fmt.colorize(color, f"{incorrect} {text}"))

        if broken:
            result.append(", ")
            result.append(fmt.colorize("RED", f"{broken} broken"))

        result.append(", ")
        result.append(f"{total} total")
        result.append(".")

        return "".join(result)
