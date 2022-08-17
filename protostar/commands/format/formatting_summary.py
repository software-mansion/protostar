from logging import Logger
from typing import List
from protostar.utils.log_color_provider import LogColorProvider
from protostar.commands.format.formatting_result import (
    FormattingResult,
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


class FormatingSummary:
    def __init__(self, logger: Logger, check: bool):
        self._logger = logger
        self._check_mode = check
        self.broken: List[BrokenFormattingResult] = []
        self.incorrect: List[IncorrectFormattingResult] = []
        self.correct: List[CorrectFormattingResult] = []

    def log_summary(self, log_color_provider: LogColorProvider):
        self._logger.info(self.format_summary(log_color_provider))

    def extend_and_log(
        self, formatting_result: FormattingResult, log_color_provider: LogColorProvider
    ):
        self.log_single_result(formatting_result, log_color_provider)
        self.extend(formatting_result)

    def log_single_result(
        self, formatting_result: FormattingResult, log_color_provider: LogColorProvider
    ):
        result: List[str] = []

        broken_header = f'[{log_color_provider.colorize("RED", "BROKEN")}]'

        correct_text = "CORRECTLY FORMATTED" if self._check_mode else "UNCHANGED"
        correct_header = f'[{log_color_provider.colorize("CYAN", correct_text)}]'

        incorrect_text = "INCORRECTLY FORMATTED" if self._check_mode else "REFORMATTED"
        incorrect_color = "YELLOW" if self._check_mode else "GREEN"
        incorrect_header = (
            f"[{log_color_provider.colorize(incorrect_color, incorrect_text)}]"
        )

        max_len = max(len(x) for x in (broken_header, correct_header, incorrect_header))
        padding = 2

        broken_header = broken_header.ljust(max_len + padding, " ")
        incorrect_header = incorrect_header.ljust(max_len + padding, " ")
        correct_header = correct_header.ljust(max_len + padding, " ")

        if isinstance(formatting_result, BrokenFormattingResult):
            result.append(broken_header)
            result.append(
                log_color_provider.colorize("GRAY", str(formatting_result.filepath))
            )
            result.append("\n")
            result.append(str(formatting_result.exception))

        elif isinstance(formatting_result, CorrectFormattingResult):
            result.append(correct_header)
            result.append(
                log_color_provider.colorize("GRAY", str(formatting_result.filepath))
            )

        elif isinstance(formatting_result, IncorrectFormattingResult):
            result.append(incorrect_header)
            result.append(str(formatting_result.filepath))

        print("".join(result))

    def extend(self, formatting_result: FormattingResult):
        if isinstance(formatting_result, BrokenFormattingResult):
            self.broken.append(formatting_result)
        elif isinstance(formatting_result, CorrectFormattingResult):
            self.correct.append(formatting_result)
        elif isinstance(formatting_result, IncorrectFormattingResult):
            self.incorrect.append(formatting_result)

    def get_file_count(self):
        return len(self.broken) + len(self.correct) + len(self.incorrect)

    def format_summary(self, log_color_provider: LogColorProvider) -> str:
        total = self.get_file_count()
        broken = len(self.broken)
        incorrect = len(self.incorrect)

        result: List[str] = [log_color_provider.bold("Summary: ")]

        text = "incorrectly formatted" if self._check_mode else "reformatted"
        color = "YELLOW" if self._check_mode else "GREEN"

        result.append(log_color_provider.colorize(color, f"{incorrect} {text}"))

        result.append(", ")
        result.append(log_color_provider.colorize("RED", f"{broken} broken"))

        result.append(", ")
        result.append(f"{total} total")

        return "".join(result)
