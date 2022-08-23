from typing import List, Callable, Any, Optional
from pathlib import Path

from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.compiler.parser_transformer import ParserError
from starkware.cairo.lang.compiler.ast.formatting_utils import FormattingError

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

    # pylint: disable=too-many-locals,too-many-arguments
    def format(
        self,
        targets: List[Path],
        check=False,
        verbose=False,
        ignore_broken=False,
        on_formatting_result: Optional[Callable[[FormattingResult], Any]] = None,
    ) -> FormattingSummary:
        summary = FormattingSummary()
        filepaths = self._get_filepaths(targets)

        if on_formatting_result is None:
            on_formatting_result = lambda result: None

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
                on_formatting_result(result)

                # Cairo formatter fixes some broken files
                # We want to disable this behavior
                continue

            if content == new_content:
                result = CorrectFormattingResult(relative_filepath)
            else:
                if not check:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(new_content)

                result = IncorrectFormattingResult(relative_filepath)

            summary.extend(result)
            if not isinstance(result, CorrectFormattingResult) or verbose:
                on_formatting_result(result)

        return summary

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
