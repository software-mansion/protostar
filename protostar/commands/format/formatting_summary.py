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
    def __init__(
        self, logger: Logger, check: bool = False, log_formatted: bool = False
    ):
        self._logger = logger
        self._check_mode = check
        self._log_formatted = log_formatted
        self.broken: List[BrokenFormattingResult] = []
        self.incorrect: List[IncorrectFormattingResult] = []
        self.correct: List[CorrectFormattingResult] = []

    def log_summary(self, log_color_provider: LogColorProvider):
        if self.get_file_count() == 0:
            self._logger.warn("No files found")
        else:
            self._logger.info(self.format_summary(log_color_provider))

    def extend_and_log(
        self, formatting_result: FormattingResult, log_color_provider: LogColorProvider
    ):
        if (
            not isinstance(formatting_result, CorrectFormattingResult)
            or self._log_formatted
        ):
            self.log_single_result(formatting_result, log_color_provider)
        self.extend(formatting_result)

    def log_single_result(
        self, formatting_result: FormattingResult, log_color_provider: LogColorProvider
    ):
        result: List[str] = []

        broken_header = self._get_broken_header(log_color_provider)
        correct_header = self._get_correct_header(self._check_mode, log_color_provider)
        incorrect_header = self._get_incorrect_header(
            self._check_mode, log_color_provider
        )

        padding = (
            max(len(x) for x in (broken_header, correct_header, incorrect_header)) + 2
        )

        broken_header = self._pad_header(broken_header, padding)
        incorrect_header = self._pad_header(incorrect_header, padding)
        correct_header = self._pad_header(correct_header, padding)

        if isinstance(formatting_result, BrokenFormattingResult):
            result.append(broken_header)
            result.append(
                self._get_formatted_path(formatting_result, log_color_provider)
            )
            result.append("\n")
            result.append(str(formatting_result.exception))

        elif isinstance(formatting_result, CorrectFormattingResult):
            result.append(correct_header)
            result.append(
                self._get_formatted_path(formatting_result, log_color_provider)
            )

        elif isinstance(formatting_result, IncorrectFormattingResult):
            result.append(incorrect_header)
            result.append(
                self._get_formatted_path(formatting_result, log_color_provider)
            )

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

        text = "unformatted" if self._check_mode else "reformatted"
        color = "YELLOW" if self._check_mode else "GREEN"

        result.append(log_color_provider.colorize(color, f"{incorrect} {text}"))

        if broken:
            result.append(", ")
            result.append(log_color_provider.colorize("RED", f"{broken} broken"))

        result.append(", ")
        result.append(f"{total} total")

        return "".join(result)

    @staticmethod
    def _get_formatted_path(
        formatting_result: FormattingResult, log_color_provider: LogColorProvider
    ) -> str:
        return log_color_provider.colorize("GRAY", str(formatting_result.filepath))

    @staticmethod
    def _get_broken_header(log_color_provider: LogColorProvider) -> str:
        return f'[{log_color_provider.colorize("RED", "BROKEN")}]'

    @staticmethod
    def _get_correct_header(check: bool, log_color_provider: LogColorProvider) -> str:
        correct_text = "FORMATTED" if check else "UNCHANGED"
        return f'[{log_color_provider.colorize("CYAN", correct_text)}]'

    @staticmethod
    def _get_incorrect_header(check: bool, log_color_provider: LogColorProvider) -> str:
        incorrect_text = "UNFORMATTED" if check else "REFORMATTED"
        incorrect_color = "YELLOW" if check else "GREEN"
        return f"[{log_color_provider.colorize(incorrect_color, incorrect_text)}]"

    @staticmethod
    def _pad_header(header: str, padding_size: int) -> str:
        return header.ljust(padding_size, " ")
