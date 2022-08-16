from logging import Logger
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass

from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.compiler.parser_transformer import ParserError

from protostar.cli import Command
from protostar.utils import log_color_provider


@dataclass
class FormatCounts:
    total = 0
    broken = 0
    reformatted = 0
    incorrectly_formatted = 0

    def format(self, check: bool) -> str:
        result = "\n"
        if check:
            result += (
                f"{self.incorrectly_formatted}/{self.total} incorrectly formatted\n"
            )
            result += f"{self.broken}/{self.total} broken\n"
        else:
            result += f"{self.reformatted}/{self.total} reformatted"
            result += f"{self.broken}/{self.total} broken\n"
        return result


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
        try:
            counts = self.format(args.target, args.check)
        except BaseException as exc:
            self._logger.error("Command failed.")
            raise exc
        self._logger.info(counts.format(args.check))

    def format(self, targets: List[str], check=False) -> FormatCounts:
        # check if works for single files

        counts = FormatCounts()
        target_path = Path(*targets)
        filepaths = [f for f in target_path.resolve().glob("**/*.cairo") if f.is_file()]

        counts.total = len(filepaths)

        for filepath in filepaths:
            try:
                content = open(filepath).read()
                new_content = parse_file(content, filepath).format()
            except ParserError as ex:
                self._logger.warn(
                    f"Cannot parse {log_color_provider.colorize('GRAY', str(filepath))}, exception:\n {ex}"
                )
                counts.broken += 1

                # Cairo formatter fixes some broken files
                # We want to disable this behaviour
                continue

            if not check:
                if content == new_content:
                    self._logger.info(
                        log_color_provider.colorize("GRAY", f"Unchanged:\t{filepath}")
                    )

                else:

                    # TODO: Check if writing fails
                    open(filepath, "w").write(new_content)
                    self._logger.info(
                        log_color_provider.bold(f"Reformatted:\t{filepath}")
                    )
                    counts.reformatted += 1

            else:
                if content != new_content:
                    self._logger.info(f"Incorrectly formatted:\t{filepath}")
                    counts.incorrectly_formatted += 1

        return counts
