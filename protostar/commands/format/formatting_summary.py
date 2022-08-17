from logging import Logger
from typing import List
from dataclasses import dataclass
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

    def log(self, log_color_provider: LogColorProvider):
        self._logger.info(self.format_files(log_color_provider))
        self._logger.info(self.format_summary(log_color_provider))

    def extend(self, formatting_result: FormattingResult):
        if isinstance(formatting_result, BrokenFormattingResult):
            self.broken.append(formatting_result)
        elif isinstance(formatting_result, CorrectFormattingResult):
            self.correct.append(formatting_result)
        elif isinstance(formatting_result, IncorrectFormattingResult):
            self.incorrect.append(formatting_result)

    def get_file_count(self):
        return len(self.broken) + len(self.correct) + len(self.incorrect)

    def format_files(self, log_color_provider: LogColorProvider) -> str:
        result: List[str] = [""]

        # Display correct at the beginning because they are not that important

        if self.correct:
            subresult: List[str] = []
            subresult.append("[")
            subresult.append(
                log_color_provider.colorize(
                    "CYAN", "CORRECTLY FORMATTED" if self._check_mode else "UNCHANGED"
                )
            )
            subresult.append("]")
            result.append("".join(subresult))

            for correct_result in self.correct:
                result.append(
                    log_color_provider.colorize("GRAY", str(correct_result.filepath))
                )

            result.append("")

        if self.broken:
            subresult: List[str] = []
            subresult.append("[")
            subresult.append(log_color_provider.colorize("RED", "BROKEN"))
            subresult.append("]")
            result.append("".join(subresult))

            for broken_result in self.broken:
                subresult: List[str] = []
                subresult.append(
                    log_color_provider.colorize("GRAY", str(broken_result.filepath))
                )
                subresult.append("\n")
                subresult.append(str(broken_result.exception))
                subresult.append("\n")
                result.append("".join(subresult))

            result.append("")

        if self.incorrect:
            subresult: List[str] = []
            subresult.append("[")
            subresult.append(
                log_color_provider.colorize(
                    "YELLOW" if self._check_mode else "GREEN",
                    "INCORRECTLY FORMATTED" if self._check_mode else "REFORMATTED",
                )
            )
            subresult.append("]")
            result.append("".join(subresult))

            for incorrect_result in self.incorrect:
                result.append(str(incorrect_result.filepath))

            result.append("")

        return "\n".join(result)

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
