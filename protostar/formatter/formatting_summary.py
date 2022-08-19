from dataclasses import dataclass, field
from typing import List
from protostar.utils.log_color_provider import log_color_provider
from protostar.formatter.formatting_result import (
    FormattingResult,
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


@dataclass
class FormattingSummary:
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

    def get_file_count(self):
        return len(self.broken) + len(self.correct) + len(self.incorrect)

    def any_unformatted_or_broken(self, check: bool):
        return bool(len(self.broken) + (len(self.incorrect) if check else 0))


def format_summary(summary: FormattingSummary, check: bool) -> str:
    total = summary.get_file_count()
    broken = len(summary.broken)
    incorrect = len(summary.incorrect)

    result: List[str] = [log_color_provider.bold("Summary: ")]

    text = "[UNFORMATTED]" if check else "[REFORMATTED]"
    color = "YELLOW" if check else "GREEN"

    result.append(log_color_provider.colorize(color, f"{incorrect} {text}"))

    if broken:
        result.append(", ")
        result.append(log_color_provider.colorize("RED", f"{broken} broken"))

    result.append(", ")
    result.append(f"{total} total")

    return "".join(result)
