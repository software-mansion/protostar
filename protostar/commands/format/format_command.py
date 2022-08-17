from logging import Logger
from typing import List, Optional, Tuple
from pathlib import Path

from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.compiler.parser_transformer import ParserError

from protostar.cli import Command, ActivityIndicator
from ...protostar_exception import ProtostarExceptionSilent
from protostar.utils import log_color_provider

from protostar.commands.format.formatting_summary import FormatingSummary
from protostar.commands.format.formatting_result import (
    BrokenFormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
)


class FormatCommand(Command):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self._logger = logger

    @property
    def example(self) -> Optional[str]:
        return "$ protostar format"

    @property
    def name(self) -> str:
        return "format"

    @property
    def description(self) -> str:
        return "Format cairo sourcecode."

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="target",
                description=("Directory to format."),
                type="str",
                is_array=True,
                is_positional=True,
                default=["."],
            ),
            Command.Argument(
                name="check",
                description="Check whether the sourcecode is formatted.",
                type="bool",
                is_required=False,
                default=False,
                short_name="c",
            ),
        ]

    async def run(self, args):
        with ActivityIndicator(
            log_color_provider.colorize(
                "GRAY", "Checking formatting" if args.check else "Reformatting files"
            )
        ):
            try:
                summary, any_unformatted_or_broken = self.format(
                    args.target, args.check
                )
            except BaseException as exc:
                self._logger.error("Command failed.")
                raise exc
        summary.log(log_color_provider)

        # set exit code to 1
        if any_unformatted_or_broken:
            raise ProtostarExceptionSilent(
                "Some files were incorrectly formatted or broken."
            )

    def format(self, targets: List[str], check=False) -> Tuple[FormatingSummary, int]:
        summary = FormatingSummary(self._logger, check)
        filepaths: List[Path] = []

        for target in targets:
            target_path = Path(target)

            if target_path.is_file():
                filepaths.append(target_path.resolve())
            else:
                filepaths.extend(
                    [f for f in target_path.resolve().glob("**/*.cairo") if f.is_file()]
                )

        summary.total = len(filepaths)
        any_unformatted_or_broken = False

        for filepath in filepaths:
            try:
                content = open(filepath).read()
                new_content = parse_file(content, filepath).format()
            except ParserError as ex:
                summary.extend(BrokenFormattingResult(filepath, ex))
                any_unformatted_or_broken = 1

                # Cairo formatter fixes some broken files
                # We want to disable this behaviour
                continue

            if content == new_content:
                summary.extend(CorrectFormattingResult(filepath))
            else:
                if check:
                    any_unformatted_or_broken = 1
                else:
                    open(filepath, "w").write(new_content)

                summary.extend(IncorrectFormattingResult(filepath))

        return summary, any_unformatted_or_broken
