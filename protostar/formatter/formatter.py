from typing import List
from pathlib import Path
from logging import Logger

from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.compiler.parser_transformer import ParserError
from starkware.cairo.lang.compiler.ast.formatting_utils import FormattingError

from protostar.formatter.formatting_result import (
    FormattingResult,
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
    format_formatting_result,
)
from protostar.formatter.formatting_summary import FormattingSummary, format_summary


class Formatter:
    def __init__(self, logger: Logger, project_root_path: Path):
        self._logger = logger
        self._project_root_path = project_root_path

    # pylint: disable=too-many-locals
    def format(
        self, targets: List[Path], check=False, verbose=False, ignore_broken=False
    ) -> bool:
        summary = FormattingSummary()
        filepaths = self._get_filepaths(targets)
        any_unformatted_or_broken = False

        for filepath in filepaths:
            relative_filepath = filepath.relative_to(self._project_root_path)

            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                new_content = parse_file(content, str(filepath)).format()
            except (ParserError, FormattingError) as ex:
                if ignore_broken:
                    continue

                result = BrokenFormattingResult(relative_filepath, ex)
                summary.extend(result)
                self._log_formatting_result(result, check, verbose)
                any_unformatted_or_broken = True

                # Cairo formatter fixes some broken files
                # We want to disable this behavior
                continue

            if content == new_content:
                result = CorrectFormattingResult(relative_filepath)
            else:
                if check:
                    any_unformatted_or_broken = True
                else:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(new_content)

                result = IncorrectFormattingResult(relative_filepath)

            summary.extend(result)
            self._log_formatting_result(result, check, verbose)

        self._log_summary(summary, check)

        return any_unformatted_or_broken

    def _log_summary(self, summary: FormattingSummary, check: bool):
        if summary.get_file_count() == 0:
            self._logger.warn("No files found")
        else:
            self._logger.info(format_summary(summary, check))

    @staticmethod
    def _log_formatting_result(
        formatting_result: FormattingResult, check: bool, verbose: bool
    ):
        if not isinstance(formatting_result, CorrectFormattingResult) or verbose:
            print(format_formatting_result(formatting_result, check))

    @staticmethod
    def _get_filepaths(targets: List[Path]):
        filepaths: List[Path] = []

        for target_path in targets:
            if target_path.is_file():
                filepaths.append(target_path.resolve())
            else:
                filepaths.extend(
                    [f for f in target_path.resolve().glob("**/*.cairo") if f.is_file()]
                )

        return filepaths
