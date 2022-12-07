from pathlib import Path
from typing import List, Callable, Any, Optional

from starkware.cairo.lang.compiler.ast.formatting_utils import FormattingError
from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.compiler.parser_transformer import ParserError

from protostar.formatter.formatting_result import (
    FormattingResult,
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)
from protostar.formatter.formatting_summary import FormattingSummary


class Formatter:
    def __init__(self, project_root_path: Path):
        self._project_root_path = project_root_path

    def format(
        self,
        file_paths: List[Path],
        check: bool = False,
        verbose: bool = False,
        ignore_broken: bool = False,
        on_formatting_result: Optional[Callable[[FormattingResult], Any]] = None,
    ) -> FormattingSummary:
        summary = FormattingSummary(checked_only=check)

        for filepath in file_paths:
            relative_filepath = filepath.relative_to(self._project_root_path)

            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                new_content = parse_file(content, str(filepath)).format()
            except (ParserError, FormattingError) as ex:
                if ignore_broken:
                    continue

                result = BrokenFormattingResult(
                    filepath=relative_filepath,
                    checked_only=check,
                    exception=ex,
                )
                summary.extend(result)

                if on_formatting_result is not None:
                    on_formatting_result(result)

                # Cairo formatter fixes some broken files
                # We want to disable this behavior
                continue

            if content == new_content:
                result = CorrectFormattingResult(
                    filepath=relative_filepath,
                    checked_only=check,
                )
            else:
                if not check:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(new_content)

                result = IncorrectFormattingResult(
                    filepath=relative_filepath,
                    checked_only=check,
                )

            summary.extend(result)
            if not isinstance(result, CorrectFormattingResult) or verbose:
                if on_formatting_result is not None:
                    on_formatting_result(result)

        return summary
