from logging import Logger
from typing import List, Optional, Tuple
from pathlib import Path

from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.compiler.parser_transformer import ParserError
from starkware.cairo.lang.compiler.ast.formatting_utils import FormattingError

from protostar.cli import Command
from protostar.protostar_exception import ProtostarExceptionSilent
from protostar.utils import log_color_provider

from protostar.commands.format.formatting_summary import FormattingSummary
from protostar.commands.format.formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


class FormatCommand(Command):
    def __init__(self, project_root_path: Path, logger: Logger) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._logger = logger

    @property
    def example(self) -> Optional[str]:
        return "$ protostar format"

    @property
    def name(self) -> str:
        return "format"

    @property
    def description(self) -> str:
        return "Format cairo source code."

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="target",
                description=("Target to format, can be a file or a directory."),
                type="str",
                is_array=True,
                is_positional=True,
                default=["."],
            ),
            Command.Argument(
                name="check",
                description=(
                    "Run in 'check' mode. Exits with 0 if input is formatted correctly."
                    "Exits with 1 if formatting is required."
                ),
                type="bool",
                is_required=False,
                default=False,
                short_name="c",
            ),
            Command.Argument(
                name="log-formatted",
                description=("Log information about already formatted files."),
                type="bool",
                is_required=False,
                default=False,
            ),
            Command.Argument(
                name="ignore-broken",
                description=("Ignore broken files."),
                type="bool",
                is_required=False,
                default=False,
            ),
        ]

    async def run(self, args):
        try:
            summary, any_unformatted_or_broken = self.format(
                args.target, args.check, args.log_formatted, args.ignore_broken
            )
        except BaseException as exc:
            self._logger.fatal("Command failed.")
            raise exc
        summary.log_summary(log_color_provider)

        # set exit code to 1
        if any_unformatted_or_broken:
            raise ProtostarExceptionSilent(
                "Some files were unformatted, impossible to format or broken."
            )

    # pylint: disable=too-many-locals
    def format(
        self, targets: List[str], check=False, log_formatted=False, ignore_broken=False
    ) -> Tuple[FormattingSummary, int]:
        summary = FormattingSummary(self._logger, check, log_formatted)
        filepaths: List[Path] = []

        for target in targets:
            target_path = Path(target)

            if target_path.is_file():
                filepaths.append(target_path.resolve())
            else:
                filepaths.extend(
                    [f for f in target_path.resolve().glob("**/*.cairo") if f.is_file()]
                )

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

                summary.extend_and_log(
                    BrokenFormattingResult(relative_filepath, ex), log_color_provider
                )
                any_unformatted_or_broken = True

                # Cairo formatter fixes some broken files
                # We want to disable this behavior
                continue

            if content == new_content:
                summary.extend_and_log(
                    CorrectFormattingResult(relative_filepath), log_color_provider
                )
            else:
                if check:
                    any_unformatted_or_broken = True
                else:
                    with open(filepath, "w", encoding="utf-8") as file:
                        file.write(new_content)

                summary.extend_and_log(
                    IncorrectFormattingResult(relative_filepath), log_color_provider
                )

        return summary, any_unformatted_or_broken
